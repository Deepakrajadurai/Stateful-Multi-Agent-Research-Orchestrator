const API_BASE = "http://localhost:8000";

function setQuestion(text) {
  document.getElementById("question").value = text.trim();
  document.getElementById("question").focus();
}

async function submitQuery() {
  const questionInput = document.getElementById("question");
  const question = questionInput.value.trim();
  if (!question) return;

  const categoryFilter = document.getElementById("categoryFilter").value;
  const yearFilter = document.getElementById("yearFilter").value;

  const metadata_filters = {};
  if (categoryFilter) metadata_filters.category = categoryFilter;
  if (yearFilter) metadata_filters.year = parseInt(yearFilter);

  const btn = document.getElementById("submitBtn");
  const spinner = document.getElementById("spinner");
  const errorEl = document.getElementById("error");
  const results = document.getElementById("results");

  btn.disabled = true;
  spinner.style.display = "block";
  errorEl.style.display = "none";
  errorEl.textContent = "";
  results.innerHTML = "";

  try {
    const resp = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, metadata_filters: Object.keys(metadata_filters).length ? metadata_filters : null })
    });

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      throw new Error(errData.detail || `API error: status ${resp.status}`);
    }
    const data = await resp.json();
    renderResults(data);
  } catch (err) {
    errorEl.style.display = "block";
    errorEl.textContent = `Error executing research graph: ${err.message}`;
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
  }
}

function formatMarkdownToHtml(markdown) {
  if (!markdown) return "";

  // Clean raw markdown tags into formatted HTML
  let html = markdown
    // Sanitize any replacement character glitched symbols
    .replace(/C/g, '°C')
    .replace(//g, "'")
    // Convert Headers
    .replace(/^### (.*$)/gim, '<h4 style="color:#a5b4fc; font-family:\'Outfit\',sans-serif; font-size:1.1rem; font-weight:700; margin-top:20px; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:6px;">$1</h4>')
    .replace(/^#### (.*$)/gim, '<h5 style="color:#c7d2fe; font-family:\'Outfit\',sans-serif; font-size:0.975rem; font-weight:600; margin-top:16px; margin-bottom:8px;">$1</h5>')
    // Convert Bold and Italics
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color:#ffffff; font-weight:600;">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em style="color:#cbd5e1;">$1</em>')
    // Convert Bullets
    .replace(/^\- (.*$)/gim, '<div style="margin-left:12px; margin-bottom:8px; padding-left:12px; border-left:2px solid rgba(99,102,241,0.4); color:#e2e8f0; line-height:1.6;">$1</div>')
    // Convert double and single line breaks cleanly
    .replace(/\n\n/g, '<div style="height:12px;"></div>')
    .replace(/\n/g, '<br/>');

  return html;
}

function renderResults(data) {
  const results = document.getElementById("results");

  const retryBadge = data.retry_count > 0
    ? `<div style="display:inline-block; background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.35); color:#fbbf24; padding:6px 14px; border-radius:9999px; font-size:0.825rem; font-weight:600; margin-bottom:24px;">🔄 Validator Feedback Loop Triggered (${data.retry_count} Recovery Pass)</div>`
    : `<div style="display:inline-block; background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.35); color:#34d399; padding:6px 14px; border-radius:9999px; font-size:0.825rem; font-weight:600; margin-bottom:24px;">✓ Passed Quality Validation on First Pass</div>`;

  // Render Trace Timeline
  const traceHtml = (data.agent_trace || []).map(t => {
    const isRetry = t.status === "RETRY_TRIGGERED" || t.status === "RECOVERY_LOOP";
    return `
      <div class="trace-step ${isRetry ? 'retry' : 'passed'}">
        <div class="trace-icon">${t.icon || '🤖'}</div>
        <div class="trace-content">
          <div class="trace-header">
            <span class="trace-title">${escapeHtml(t.title || t.agent)}</span>
            <span class="trace-meta">${t.latency_sec ? t.latency_sec + 's' : ''}</span>
          </div>
          <div class="trace-detail">${escapeHtml(t.detail || '')}</div>
          ${t.metrics ? `<div class="trace-badge">${escapeHtml(t.metrics)}</div>` : ''}
        </div>
      </div>
    `;
  }).join("");

  // Render Sub-questions
  const subQuestionsHtml = (data.sub_questions || []).map(sq =>
    `<div class="sub-q">${escapeHtml(sq)}</div>`
  ).join("");

  // Clean answer text: format markdown to HTML without raw markup tags
  const cleanAnswerHtml = formatMarkdownToHtml(data.answer);

  // Render Provenance Metadata Cards
  const provenanceHtml = (data.sources_metadata && data.sources_metadata.length > 0)
    ? data.sources_metadata.map(meta => `
        <div class="prov-card">
          <div class="prov-header">SOURCE: ${escapeHtml(meta.source || 'European Commission - JRC')}</div>
          <div class="prov-title">${escapeHtml(meta.title)}</div>
          <div class="prov-tags">
            <span class="prov-tag">Category: ${escapeHtml(meta.category || 'general')}</span>
            <span class="prov-tag">Year: ${meta.publication_year || 2023}</span>
            <span class="prov-tag">Page: ${meta.page || 1}</span>
          </div>
          ${meta.url ? `<a href="${escapeHtml(meta.url)}" target="_blank" style="color:#818cf8; font-size:0.775rem; text-decoration:none; margin-top:4px; display:inline-block;">🔗 View Original JRC Dataset Metadata</a>` : ''}
        </div>
      `).join("")
    : (data.sources || []).map(s => `
        <div class="prov-card">
          <div class="prov-header">SOURCE: European Commission - JRC</div>
          <div class="prov-title">${escapeHtml(s)}</div>
        </div>
      `).join("") || `<div style="color:var(--text-dim); font-size:0.875rem;">No explicit dataset citations returned.</div>`;

  results.innerHTML = `
    ${retryBadge}

    <div class="card">
      <h3>Agent Execution Trace</h3>
      <div class="trace-timeline">
        ${traceHtml || '<div style="color:var(--text-dim);">No trace steps recorded.</div>'}
      </div>
    </div>

    <div class="card">
      <h3>Planner Sub-Questions (${(data.sub_questions || []).length})</h3>
      ${subQuestionsHtml}
    </div>

    <div class="card">
      <h3>Synthesised Evidence Report</h3>
      <div class="answer">${cleanAnswerHtml}</div>
    </div>

    <div class="card">
      <h3>Document Provenance & Citations (${(data.sources_metadata || data.sources || []).length})</h3>
      <div class="provenance-grid">
        ${provenanceHtml}
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

document.getElementById("question").addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    submitQuery();
  }
});
