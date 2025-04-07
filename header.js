function loadHeader(pageId) {
    const headerPromise = fetch("header.html")
    const headerHtmlPromise = headerPromise.then(
        (response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
    headerHtmlPromise.then(
        (html) => {
            let header = document.querySelector("#header");
            header.innerHTML = html;
            let currentPageLink = document.querySelector(`#${pageId}`);
            if (currentPageLink) {
                let highlightingElement = document.createElement("b");
                currentPageLink.parentNode.insertBefore(highlightingElement, currentPageLink)
                highlightingElement.appendChild(currentPageLink)
            }
        })
    .then(

    )
    .catch((error) => {
        console.error(`Error loading ${"header.html"}:`, error);
    });
}