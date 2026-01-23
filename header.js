async function loadHeaderHtml(pageId) {
    const response = await fetch("header.html")
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.text();
}

function highlightCurrentPage(pageId) {
    // Sanitize pageId to prevent DOM-based XSS - only allow alphanumeric, hyphen, underscore
    const sanitizedPageId = pageId.replace(/[^a-zA-Z0-9_-]/g, '');
    if (!sanitizedPageId) return;

    let currentPageLink = document.getElementById(sanitizedPageId)
    if (currentPageLink) {
        let highlightingElement = document.createElement("b")
        currentPageLink.parentNode.insertBefore(highlightingElement, currentPageLink)
        highlightingElement.appendChild(currentPageLink)
    }
}

function loadHeader(pageId) {
    let header = document.querySelector("#header")
    htmlPromise = loadHeaderHtml(pageId)
    htmlPromise.then((html) => {
        // Use DOMParser to safely parse HTML instead of innerHTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Clear existing content and append parsed nodes
        header.textContent = '';
        Array.from(doc.body.childNodes).forEach(node => {
            header.appendChild(node.cloneNode(true));
        });

        highlightCurrentPage(pageId)
    })
}

function header() {
    pageId = document.querySelector('meta[name="page"]').content
    document.addEventListener("DOMContentLoaded", () => {loadHeader(pageId)});
}

header()