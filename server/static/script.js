const algorithmInput = document.getElementById("algorithms");
const sourceInput = document.getElementById("source");
const targetInput = document.getElementById("target");
const searchButton = document.getElementById("searchButton");
const resultBox = document.getElementsByClassName("result")[0];
const sourceText = document.getElementById("source-text");
const targetText = document.getElementById("target-text");

const timeText = document.getElementById("time");
const nodesExpandedText = document.getElementById("nodes");
const pathLengthText = document.getElementById("path-length");
const peakMemoryText = document.getElementById("memory");
const statusText = document.getElementById("status");
const uiWallTimeText = document.getElementById("ui-wall-time");
const serverWallTimeText = document.getElementById("server-wall-time");
const serverImportTimeText = document.getElementById("server-import-time");
const serverAlgoCallTimeText = document.getElementById("server-algo-call-time");
const serverSaveCacheTimeText = document.getElementById("server-save-cache-time");

searchButton.addEventListener("click", search);

let latestRequestId = 0;

async function search() {
  const requestId = ++latestRequestId;

  const algorithm = algorithmInput.value;
  const sourceValue = sourceInput.value;
  const targetValue = targetInput.value;

  const context = {
    algorithm: algorithm,
    sourceValue: sourceValue,
    targetValue: targetValue,
    timeoutSeconds: 300,
    logEvery: 10,
  };

  try {
    const uiStart = performance.now();
    resultBox.style.display = "block";
    sourceText.innerText = sourceValue;
    targetText.innerText = targetValue;
    searchButton.setAttribute("disabled", "");
    statusText.innerText = "running";
    if (uiWallTimeText) uiWallTimeText.innerText = "-";
    if (serverWallTimeText) serverWallTimeText.innerText = "-";
    if (serverImportTimeText) serverImportTimeText.innerText = "-";
    if (serverAlgoCallTimeText) serverAlgoCallTimeText.innerText = "-";
    if (serverSaveCacheTimeText) serverSaveCacheTimeText.innerText = "-";

    const response = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(context),
    });

    console.log("Fetch response status:", response.status);

    const data = await response.json();

    // Ignore stale responses (e.g. a request canceled by a newer click).
    if (requestId !== latestRequestId) return;

    if (!response.ok) {
      statusText.innerText = data["status"] || "error";
      if (uiWallTimeText) uiWallTimeText.innerText = ((performance.now() - uiStart) / 1000).toFixed(3);
      return;
    }

    timeText.innerText = data["time_taken"];
    nodesExpandedText.innerText = data["nodes_expanded"];
    pathLengthText.innerText = data["path_length"];
    peakMemoryText.innerText = data["peak_memory_mb"];
    statusText.innerText = data["status"];

    if (uiWallTimeText) uiWallTimeText.innerText = ((performance.now() - uiStart) / 1000).toFixed(3);
    const serverSeconds = data?.timings?.worker_total_seconds;
    if (serverWallTimeText && typeof serverSeconds === "number") {
      serverWallTimeText.innerText = serverSeconds.toFixed(3);
    }
    const importSeconds = data?.timings?.import_seconds;
    if (serverImportTimeText && typeof importSeconds === "number") {
      serverImportTimeText.innerText = importSeconds.toFixed(3);
    }
    const algoCallSeconds = data?.timings?.algorithm_call_seconds;
    if (serverAlgoCallTimeText && typeof algoCallSeconds === "number") {
      serverAlgoCallTimeText.innerText = algoCallSeconds.toFixed(3);
    }
    const saveCacheSeconds = data?.timings?.save_cache_seconds;
    if (serverSaveCacheTimeText && typeof saveCacheSeconds === "number") {
      serverSaveCacheTimeText.innerText = saveCacheSeconds.toFixed(3);
    }

    // path rendering
    const pathContainer = document.getElementById("path");
    pathContainer.innerHTML = "";

    const path = data["path"];

    path.forEach((node, index) => {
      // create node
      const nodeEl = document.createElement("div");
      nodeEl.className = "path-node";
      nodeEl.innerText = node;

      // optional: open Wikipedia on click
      nodeEl.onclick = () => {
        const url = `https://en.wikipedia.org/wiki/${encodeURIComponent(node)}`;
        window.open(url, "_blank");
      };

      pathContainer.appendChild(nodeEl);

      // add arrow (except last)
      if (index < path.length - 1) {
        const arrow = document.createElement("span");
        arrow.className = "path-arrow";
        arrow.innerText = "→";
        pathContainer.appendChild(arrow);
      }
    });

    console.log(data);
  } catch (err) {
    if (requestId !== latestRequestId) return;
    console.error(err);
    statusText.innerText = "error";
  } finally {
    if (requestId === latestRequestId) {
      searchButton.removeAttribute("disabled");
    }
  }
}
