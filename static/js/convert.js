// The upload box: pick or drop a file, send it to /convert, download the result.
(function () {
  const drop = document.getElementById('drop');
  if (!drop) return;
  const input = document.getElementById('file'),
        fname = document.getElementById('fname'),
        go = document.getElementById('go'),
        status = document.getElementById('status');
  let chosen = null;
  // On the DOC <-> DOCX page (data-mode="word-format") the other Word format is
  // requested; everywhere else Word becomes PDF and PDF becomes Word.
  const wordFormat = document.querySelector('[data-mode="word-format"]') !== null;

  function target(name) {
    if (!wordFormat) return null;
    if (/\.docx$/i.test(name)) return 'doc';
    if (/\.doc$/i.test(name)) return 'docx';
    return null;
  }
  function direction(name) {
    if (wordFormat) return /\.docx$/i.test(name) ? 'docx-to-doc' : 'doc-to-docx';
    return /\.pdf$/i.test(name) ? 'pdf-to-word' : 'word-to-pdf';
  }
  function track(props) {
    // Anonymous usage count; never includes the file name or contents.
    if (window.sdTrack) window.sdTrack('convert', props);
  }
  function setFile(f) {
    chosen = f;
    if (f) {
      fname.textContent = 'Selected: ' + f.name;
      go.disabled = false;
      status.textContent = '';
      status.className = 'status';
    }
  }

  input.addEventListener('change', e => setFile(e.target.files[0]));
  ['dragover', 'dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('drag'); }));
  drop.addEventListener('drop', e => { if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); });

  go.addEventListener('click', async () => {
    if (!chosen) return;
    if (wordFormat && !target(chosen.name)) {
      status.textContent = 'Please choose a .doc or .docx file.';
      status.className = 'status err';
      return;
    }
    const dir = direction(chosen.name);
    const started = Date.now();
    go.disabled = true;
    status.className = 'status';
    status.innerHTML = '<span class="spin"></span>Converting…';
    const fd = new FormData();
    fd.append('file', chosen);
    if (target(chosen.name)) fd.append('target', target(chosen.name));
    try {
      const r = await fetch('/convert', { method: 'POST', body: fd });
      if (!r.ok) {
        let msg = 'Conversion failed';
        try { msg = (await r.json()).error || msg; } catch (_) {}
        status.textContent = msg;
        status.className = 'status err';
        go.disabled = false;
        track({ direction: dir, result: r.status === 429 ? 'rate-limited' : 'failed', status: String(r.status) });
        return;
      }
      const blob = await r.blob();
      const cd = r.headers.get('Content-Disposition') || '';
      const m = cd.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
      const name = m ? decodeURIComponent(m[1]) : 'converted';
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = name; a.click();
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      status.textContent = 'Done. Your download has started, and the file has been deleted from our server.';
      status.className = 'status ok';
      track({ direction: dir, result: 'ok', seconds: String(Math.round((Date.now() - started) / 1000)) });
    } catch (err) {
      status.textContent = 'Network error, please try again.';
      status.className = 'status err';
      track({ direction: dir, result: 'network-error' });
    }
    go.disabled = false;
  });
})();
