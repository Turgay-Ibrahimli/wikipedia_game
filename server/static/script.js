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

searchButton.addEventListener("click", search);

async function search() {
  const algorithm = algorithmInput.value;
  const sourceValue = sourceInput.value;
  const targetValue = targetInput.value;

  const context = {
    algorithm: algorithm,
    sourceValue: sourceValue,
    targetValue: targetValue,
  };

  try {
    resultBox.style.display = "block";
    sourceText.innerText = sourceValue;
    targetText.innerText = targetValue;
    searchButton.setAttribute("disabled", "");

    const response = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(context),
    });

    console.log("Fetch response status:", response.status);


    const data = await response.json();

    timeText.innerText = data["time_taken"];
    nodesExpandedText.innerText = data["nodes_expanded"];
    pathLengthText.innerText = data["path_length"];
    peakMemoryText.innerText = data["peak_memory_mb"];
    statusText.innerText = data["status"];

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
    searchButton.removeAttribute("disabled");
    console.error(err);
  } finally {
    searchButton.removeAttribute("disabled");
  }
}
