// Job Search Hub: Interview page. The browser speaks the questions and turns your spoken answer
// into text; hub.py asks Claude for the next question and for STAR feedback.
const INTERVIEWER_NAME = 'Interviewer'; // give your interviewer a name
const VOICE_RATE = 1;                    // 0.8 = slower, 1.2 = faster

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
let hub = null;
let session = null; // { job, total, asked: [], answers: [] }

async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}

// ---- speaking and listening (built into Chrome and Edge)
function say(text) {
  if (!$('#speak').checked || !window.speechSynthesis) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.rate = VOICE_RATE;
  speechSynthesis.speak(u);
}

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let listener = null;
let listening = false;
if (!Recognition) {
  $('#voice-note').textContent = "This browser can't listen. Type your answers, or open the hub in Chrome or Edge.";
}

function startListening() {
  if (!Recognition) { $('#mic-note').textContent = 'Type your answer below.'; return; }
  speechSynthesis.cancel();
  const before = $('#answer').value.trim();
  listener = new Recognition();
  listener.lang = 'en-US';
  listener.continuous = true;
  listener.interimResults = true;
  listener.onresult = (e) => {
    let heard = '';
    for (const r of e.results) heard += r[0].transcript;
    $('#answer').value = (before ? before + ' ' : '') + heard.trim();
  };
  listener.onerror = (e) => { $('#mic-note').textContent = e.error === 'not-allowed' ? 'Allow the microphone in Chrome, then try again.' : 'Listening stopped. Click to start again.'; };
  listener.onend = () => { listening = false; $('#mic').classList.remove('on'); $('#mic').textContent = '🎤 Start talking'; };
  listener.start();
  listening = true;
  $('#mic').classList.add('on');
  $('#mic').textContent = '⏹ Stop';
  $('#mic-note').textContent = 'Listening… click Stop when you finish your answer.';
}

$('#mic').addEventListener('click', () => {
  if (listening) { listener.stop(); $('#mic-note').textContent = 'Check your answer, fix any words, then ask for feedback.'; }
  else startListening();
});

// ---- interview flow
async function askNext() {
  const n = session.asked.length + 1;
  $('#progress').textContent = `Question ${n} of ${session.total}`;
  $('#question').textContent = 'Thinking of a question…';
  $('#answer').value = '';
  $('#feedback').hidden = true;
  $('#next').hidden = true;
  $('#finish').hidden = session.answers.length === 0;
  try {
    const { question } = await api('/api/interview/question', { job: session.job, asked: session.asked });
    session.asked.push(question);
    $('#question').textContent = question;
    say(question);
  } catch (e) { $('#question').textContent = e.message; }
}

function showFeedback(f) {
  const parts = ['situation', 'task', 'action', 'result'];
  $('#feedback').innerHTML = `<h3>STAR score: ${f.score}/5</h3>
    <div class="star">${parts.map((p) => `<div class="${f[p].present ? '' : 'missing'}"><b>${f[p].present ? '✓' : '✗'} ${p[0].toUpperCase() + p.slice(1)}</b>${esc(f[p].comment)}</div>`).join('')}</div>
    <p><strong>What you did well:</strong> ${esc(f.strength)}</p>
    <p><strong>Try next time:</strong> ${esc(f.improve)}</p>
    <details><summary>A stronger version, using only what you said</summary><p>${esc(f.stronger_version)}</p></details>`;
  $('#feedback').hidden = false;
}

$('#start').addEventListener('click', () => {
  const id = Number($('#job').value);
  const job = hub.jobs.find((j) => j.id === id) || null;
  session = { job, total: Number($('#count').value), asked: [], answers: [] };
  $('#interviewer-name').textContent = INTERVIEWER_NAME + (job ? ` · ${job.employer}` : '');
  $('#session').hidden = false;
  askNext();
});
$('#repeat').addEventListener('click', () => say($('#question').textContent));
$('#feedback-btn').addEventListener('click', async () => {
  if (listening) listener.stop();
  const answer = $('#answer').value.trim();
  const question = session.asked[session.asked.length - 1];
  $('#feedback-btn').disabled = true;
  $('#wait').textContent = 'Your coach is reading your answer…';
  try {
    const { feedback } = await api('/api/interview/feedback', { job: session.job, question, answer });
    session.answers.push({ question, answer, feedback });
    showFeedback(feedback);
    const more = session.asked.length < session.total;
    $('#next').hidden = !more;
    $('#finish').hidden = false;
  } catch (e) { alert(e.message); }
  $('#feedback-btn').disabled = false;
  $('#wait').textContent = '';
});
$('#next').addEventListener('click', askNext);
$('#finish').addEventListener('click', async () => {
  try {
    await api('/api/interview/save', { job_title: session.job ? `${session.job.title}, ${session.job.employer}` : 'General practice', answers: session.answers });
    $('#session').hidden = true;
    speechSynthesis.cancel();
    await load();
  } catch (e) { alert(e.message); }
});

function renderHistory() {
  if (!hub.interviews.length) return;
  $('#history').innerHTML = '<table><tr><th>Date</th><th>Job</th><th>Answers</th><th>Average STAR score</th></tr>' +
    hub.interviews.map((s) => {
      const avg = s.answers.length ? (s.answers.reduce((a, x) => a + x.feedback.score, 0) / s.answers.length).toFixed(1) : '–';
      return `<tr><td>${esc(s.date)}</td><td>${esc(s.job)}</td><td>${s.answers.length}</td><td>${avg} / 5</td></tr>`;
    }).join('') + '</table><p class="note">Your answers and feedback are saved in data/interviews/.</p>';
}

async function load() {
  hub = await api('/api/hub');
  const top = hub.top10.map((id) => hub.jobs.find((j) => j.id === id)).filter(Boolean);
  $('#job').innerHTML = '<option value="">General practice</option>' +
    top.map((j) => `<option value="${j.id}">${esc(j.title)}, ${esc(j.employer)}</option>`).join('');
  renderHistory();
}

load().catch((e) => document.querySelector('main').insertAdjacentHTML('afterbegin', `<p class="error">${esc(e.message)} Is hub.py running?</p>`));
