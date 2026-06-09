const elements = {
  reliabilityScore: document.querySelector("#reliabilityScore"),
  openIssues: document.querySelector("#openIssues"),
  resolvedIssues: document.querySelector("#resolvedIssues"),
  coverageValue: document.querySelector("#coverageValue"),
  pipelineMeta: document.querySelector("#pipelineMeta"),
  pipelineStatus: document.querySelector("#pipelineStatus"),
  pipelineCanvas: document.querySelector("#pipelineCanvas"),
  stageList: document.querySelector("#stageList"),
  issueCount: document.querySelector("#issueCount"),
  issueList: document.querySelector("#issueList"),
  issueForm: document.querySelector("#issueForm"),
  seedButton: document.querySelector("#seedButton"),
  runPipelineButton: document.querySelector("#runPipelineButton"),
  codeBlock: document.querySelector("#codeBlock"),
  codeTabs: document.querySelectorAll("[data-code-tab]"),
};

const state = {
  pipeline: null,
  selectedCodeTab: "sample_code",
};

const severityLabels = {
  low: "low",
  medium: "medium",
  high: "high",
  critical: "critical",
};

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

function formatPercent(value) {
  return `${Number(value).toFixed(value % 1 === 0 ? 0 : 1)}%`;
}

async function refreshSummary() {
  const summary = await requestJson("/quality-summary");
  elements.reliabilityScore.textContent = formatPercent(summary.reliability_score);
  elements.openIssues.textContent = summary.open_issues;
  elements.resolvedIssues.textContent = summary.resolved_issues;
}

async function refreshIssues() {
  const issues = await requestJson("/issues");
  elements.issueCount.textContent = issues.length;

  if (issues.length === 0) {
    elements.issueList.innerHTML =
      '<div class="empty-state">Список дефектів порожній</div>';
    return;
  }

  elements.issueList.innerHTML = issues
    .map(
      (issue) => `
        <article class="issue-row">
          <div>
            <p class="issue-title">${escapeHtml(issue.title)}</p>
            <div class="issue-meta">
              <span class="severity ${issue.severity}">${severityLabels[issue.severity]}</span>
              <span class="state ${issue.status}">${issue.status}</span>
              <span>${escapeHtml(issue.service)}</span>
            </div>
          </div>
          ${
            issue.status === "open"
              ? `<button class="button secondary" data-resolve-id="${issue.id}" type="button">Закрити</button>`
              : ""
          }
        </article>
      `,
    )
    .join("");
}

function renderPipeline(report) {
  state.pipeline = report;
  elements.coverageValue.textContent = formatPercent(report.coverage_percent);
  elements.pipelineMeta.textContent = `${report.branch} · ${report.commit}`;
  elements.pipelineStatus.textContent = report.passed ? "Успішно" : "Помилка";
  elements.pipelineStatus.classList.toggle("passed", report.passed);
  elements.stageList.innerHTML = report.stages
    .map(
      (stage) => `
        <article class="stage-row">
          <div>
            <div class="stage-name">${escapeHtml(stage.name)}</div>
            <code>${escapeHtml(stage.command)}</code>
          </div>
          <span class="state ${stage.status}">${stage.duration_ms} ms</span>
        </article>
      `,
    )
    .join("");
  renderPipelineCanvas(report.stages);
  renderCodeBlock();
}

function renderPipelineCanvas(stages) {
  const canvas = elements.pipelineCanvas;
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));

  const context = canvas.getContext("2d");
  context.scale(ratio, ratio);
  context.clearRect(0, 0, rect.width, rect.height);

  const padding = Math.min(60, rect.width * 0.08);
  const centerY = rect.height / 2;
  const step = stages.length > 1 ? (rect.width - padding * 2) / (stages.length - 1) : 0;

  context.lineWidth = 6;
  context.strokeStyle = "#d7dee8";
  context.beginPath();
  context.moveTo(padding, centerY);
  context.lineTo(rect.width - padding, centerY);
  context.stroke();

  stages.forEach((stage, index) => {
    const x = padding + step * index;
    const isPassed = stage.status === "passed";

    context.beginPath();
    context.arc(x, centerY, 26, 0, Math.PI * 2);
    context.fillStyle = isPassed ? "#dcfce7" : "#fee2e2";
    context.fill();
    context.lineWidth = 3;
    context.strokeStyle = isPassed ? "#15803d" : "#b91c1c";
    context.stroke();

    context.fillStyle = isPassed ? "#15803d" : "#b91c1c";
    context.font = "700 22px Inter, system-ui, sans-serif";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(isPassed ? "✓" : "!", x, centerY);

    context.fillStyle = "#1f2937";
    context.font = "800 13px Inter, system-ui, sans-serif";
    context.fillText(stage.name, x, centerY + 50);
  });
}

function renderCodeBlock() {
  if (!state.pipeline) {
    elements.codeBlock.textContent = "";
    return;
  }

  elements.codeBlock.textContent = state.pipeline[state.selectedCodeTab];
}

async function runPipeline() {
  elements.runPipelineButton.disabled = true;
  elements.runPipelineButton.textContent = "Виконується...";

  try {
    const report = await requestJson("/demo/pipeline");
    renderPipeline(report);
  } finally {
    elements.runPipelineButton.disabled = false;
    elements.runPipelineButton.textContent = "Запустити pipeline";
  }
}

async function refreshDashboard() {
  await Promise.all([refreshSummary(), refreshIssues()]);
  await runPipeline();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

elements.issueForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(elements.issueForm);

  await requestJson("/issues", {
    method: "POST",
    body: JSON.stringify({
      title: formData.get("title"),
      service: formData.get("service"),
      severity: formData.get("severity"),
    }),
  });

  elements.issueForm.reset();
  document.querySelector("#issueService").value = "core";
  await refreshDashboard();
});

elements.issueList.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-resolve-id]");
  if (!button) {
    return;
  }

  await requestJson(`/issues/${button.dataset.resolveId}/resolve`, {
    method: "PATCH",
  });
  await refreshDashboard();
});

elements.seedButton.addEventListener("click", async () => {
  await requestJson("/demo/seed", { method: "POST" });
  await refreshDashboard();
});

elements.runPipelineButton.addEventListener("click", runPipeline);

elements.codeTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    state.selectedCodeTab = tab.dataset.codeTab;
    elements.codeTabs.forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    renderCodeBlock();
  });
});

window.addEventListener("resize", () => {
  if (state.pipeline) {
    renderPipelineCanvas(state.pipeline.stages);
  }
});

refreshDashboard();
