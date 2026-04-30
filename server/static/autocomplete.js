function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

async function fetchSuggestions(query) {
  if (!query) return [];

  const url = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${encodeURIComponent(query)}&limit=5&namespace=0&format=json&origin=*`;

  const res = await fetch(url);
  const data = await res.json();

  return data[1]; // list of titles
}

function setupAutocomplete(inputEl, suggestionsEl) {
  inputEl.addEventListener("input", debounce(async () => {
    const query = inputEl.value.trim();

    if (query.length < 2) {
      suggestionsEl.innerHTML = "";
      return;
    }

    const suggestions = await fetchSuggestions(query);

    suggestionsEl.innerHTML = "";

    suggestions.forEach(title => {
      const item = document.createElement("div");
      item.className = "suggestion-item";
      item.innerText = title;

      item.onclick = () => {
        inputEl.value = title;
        suggestionsEl.innerHTML = "";
      };

      suggestionsEl.appendChild(item);
    });
  }, 300));
}

setupAutocomplete(
  document.getElementById("source"),
  document.getElementById("source-suggestions")
);

setupAutocomplete(
  document.getElementById("target"),
  document.getElementById("target-suggestions")
);