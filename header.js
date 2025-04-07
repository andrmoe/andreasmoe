async function loadHeaderHtml(pageId) {
    const response = await fetch("header.html")
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.text();
}

function highlightCurrentPage(pageId) {
    let currentPageLink = document.querySelector(`#${pageId}`)
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
        header.innerHTML = html
        highlightCurrentPage(pageId)
    })
}