// Job Search Hub: Jobs page. Reads your data from hub.py and saves your changes back to data/.
const STATUSES = ['Interested', 'Applied', 'Interview', 'Offer', 'Not selected', 'Withdrew'];
const COLUMNS = ['Company', 'Role', 'Link', 'QUICK HIRE', 'Date applied', 'Status', 'Follow-up date', 'Interview date', 'Offer date', 'Notes'];
const DATE_COLUMNS = ['Date applied', 'Follow-up date', 'Interview date', 'Offer date'];
let hub = null;

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const safeLink = (u) => (/^https?:\/\//i.test(u || '') ? u : '');

async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}

function renderStats() {
  const top = hub.jobs.filter((j) => hub.top10.includes(j.id));
  const applied = hub.tracker.filter((r) => r.Status && r.Status !== 'Interested').length;
  const scores = hub.interviews.flatMap((s) => s.answers.map((a) => a.feedback.score));
  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : '–';
  const stats = [
    [hub.jobs.length, 'openings found'],
    [`${top.filter((j) => j.student_check.checked).length}/${top.length}`, 'top jobs I checked'],
    [hub.tracker.length, 'jobs in my tracker'],
    [applied, 'applications sent'],
    [hub.interviews.length, 'practice interviews'],
    [avg, 'average STAR score (of 5)'],
  ];
  $('#stats').innerHTML = stats.map(([n, label]) => `<div class="card stat"><b>${esc(n)}</b><span>${esc(label)}</span></div>`).join('');
}

function renderProfile() {
  const p = hub.profile;
  if (!p) return;
  $('#profile').innerHTML = `<p>${esc(p.summary)}</p>
    <p><strong>Looking for:</strong> ${esc(p.target_roles.join(', '))} · <strong>Where:</strong> ${esc(p.location)}</p>
    <p><strong>Must-haves:</strong> ${esc(p.must_haves.join(' · '))}</p>
    <p><strong>Nice-to-haves:</strong> ${esc(p.nice_to_haves.join(' · ') || 'none listed')}</p>`;
}

function jobCard(j, rank) {
  const status = { met: 'met', 'not met': 'not', unknown: 'unknown' };
  const c = j.student_check;
  const link = safeLink(j.link);
  return `<article class="card job" data-id="${j.id}">
    <div class="score"><b>${j.fit_score}</b>/10</div>
    <h3>${rank}. ${esc(j.title)}</h3>
    <p class="where">${esc(j.employer)} · ${esc(j.location)}${j.pay ? ' · ' + esc(j.pay) : ''}</p>
    <div class="chips">
      ${j.quick_hire ? '<span class="chip quick">QUICK HIRE</span>' : ''}
      <span class="chip">${esc(j.label)}</span><span class="chip">${esc(j.chance)} chance</span>
      <span class="chip">${esc(j.source)}</span>
    </div>
    <p>${esc(j.why)}</p>
    <ul class="musts">${j.must_haves.map((m) => `<li class="${status[m.status]}" title="${esc(m.why)}">${esc(m.must_have)}</li>`).join('')}</ul>
    ${j.gaps.length ? `<p class="gaps"><strong>Gaps:</strong> ${esc(j.gaps.join('; '))}</p>` : ''}
    <div class="row">
      ${link ? `<a class="btn light" href="${esc(link)}" target="_blank" rel="noopener">Open listing</a>` : '<span class="note">No link: search for it yourself.</span>'}
      <button class="light" data-act="track">Add to tracker</button>
    </div>
    <div class="check ${c.checked ? 'done' : ''}">
      <label><input type="checkbox" data-f="checked" ${c.checked ? 'checked' : ''}> I opened it and checked it against my must-haves</label>
      <div class="row">
        <select data-f="agree"><option value="1" ${c.agree ? 'selected' : ''}>I agree with this ranking</option>
          <option value="0" ${c.agree ? '' : 'selected'}>I don't agree</option></select>
      </div>
      <textarea data-f="note" rows="2" placeholder="What did the agent get right or wrong? (your own words)">${esc(c.note)}</textarea>
      <div class="row"><button data-act="check">Save my check</button><span class="note" data-msg></span></div>
    </div>
  </article>`;
}

function renderJobs() {
  const top = hub.top10.map((id) => hub.jobs.find((j) => j.id === id)).filter(Boolean);
  if (top.length) $('#top10').innerHTML = top.map((j, i) => jobCard(j, i + 1)).join('');
  const others = hub.jobs.filter((j) => !hub.top10.includes(j.id));
  $('#others div').innerHTML = others.length
    ? '<ul>' + others.map((j) => `<li><strong>${esc(j.title)}</strong>, ${esc(j.employer)}: <span class="chip ${j.label === 'scam' ? 'bad' : ''}">${esc(j.label)}</span> ${esc(j.why)}</li>`).join('') + '</ul>'
    : '<p class="empty">None.</p>';
}

function renderTracker() {
  const head = '<tr>' + COLUMNS.map((c) => `<th>${esc(c)}</th>`).join('') + '<th></th></tr>';
  const rows = hub.tracker.map((r, i) => '<tr>' + COLUMNS.map((c) => {
    if (c === 'Status') return `<td><select data-row="${i}" data-col="${c}">${STATUSES.map((s) => `<option ${r[c] === s ? 'selected' : ''}>${s}</option>`).join('')}</select></td>`;
    const type = DATE_COLUMNS.includes(c) ? 'date' : 'text';
    return `<td><input type="${type}" data-row="${i}" data-col="${esc(c)}" value="${esc(r[c])}"></td>`;
  }).join('') + `<td><button class="light" data-del="${i}" title="Remove this row">✕</button></td></tr>`).join('');
  $('#tracker').innerHTML = head + (rows || `<tr><td colspan="${COLUMNS.length + 1}" class="empty">Add jobs from your top 10, or add one you found yourself.</td></tr>`);
}

function renderDocs() {
  $('#doc-list').innerHTML = hub.documents.length
    ? hub.documents.map((d) => `<li><button class="light" data-folder="${esc(d.folder)}" data-name="${esc(d.name)}">${esc(d.title)}</button></li>`).join('')
    : '<li class="empty">No documents yet.</li>';
}

function render() {
  renderStats(); renderProfile(); renderJobs(); renderTracker(); renderDocs();
  if (hub.profile) $('#greeting').textContent = `Searching for: ${hub.profile.target_roles.join(', ')}`;
}

async function load() {
  try { hub = await api('/api/hub'); render(); }
  catch (e) { document.querySelector('main').insertAdjacentHTML('afterbegin', `<p class="error">${esc(e.message)} Is hub.py running?</p>`); }
}

$('#top10').addEventListener('click', async (e) => {
  const btn = e.target.closest('button');
  if (!btn) return;
  const card = btn.closest('.job');
  const id = Number(card.dataset.id);
  try {
    if (btn.dataset.act === 'track') {
      hub.tracker = (await api('/api/tracker/add', { id })).tracker;
      renderTracker(); renderStats();
      btn.textContent = 'In tracker ✓';
    } else if (btn.dataset.act === 'check') {
      const check = {
        checked: card.querySelector('[data-f=checked]').checked,
        agree: card.querySelector('[data-f=agree]').value === '1',
        note: card.querySelector('[data-f=note]').value,
      };
      await api('/api/check', { id, ...check });
      hub.jobs.find((j) => j.id === id).student_check = check;
      card.querySelector('.check').classList.toggle('done', check.checked);
      card.querySelector('[data-msg]').textContent = 'Saved.';
      renderStats();
    }
  } catch (err) { alert(err.message); }
});

function readTracker() {
  document.querySelectorAll('#tracker [data-row]').forEach((el) => { hub.tracker[el.dataset.row][el.dataset.col] = el.value; });
}

$('#tracker').addEventListener('click', (e) => {
  const del = e.target.closest('[data-del]');
  if (del && confirm('Remove this job from your tracker?')) { readTracker(); hub.tracker.splice(Number(del.dataset.del), 1); renderTracker(); }
});
$('#add-row').addEventListener('click', () => {
  readTracker();
  hub.tracker.push(Object.fromEntries(COLUMNS.map((c) => [c, c === 'Status' ? 'Interested' : ''])));
  renderTracker();
});
$('#save-tracker').addEventListener('click', async () => {
  readTracker();
  try { hub.tracker = (await api('/api/tracker', { rows: hub.tracker })).tracker; renderTracker(); renderStats(); $('#tracker-msg').textContent = 'Saved to data/tracker.csv.'; }
  catch (err) { $('#tracker-msg').textContent = err.message; }
});
$('#download').addEventListener('click', () => {
  readTracker();
  const cell = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const csv = [COLUMNS.map(cell).join(',')].concat(hub.tracker.map((r) => COLUMNS.map((c) => cell(r[c])).join(','))).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  a.download = 'job-tracker.csv';
  a.click();
});
$('#doc-list').addEventListener('click', async (e) => {
  const btn = e.target.closest('button');
  if (!btn) return;
  try {
    const doc = await api(`/api/document?folder=${encodeURIComponent(btn.dataset.folder)}&name=${encodeURIComponent(btn.dataset.name)}`);
    $('#doc-view').textContent = doc.text;
  } catch (err) { $('#doc-view').textContent = err.message; }
});

load();
