/* The lab only changes its own sample box; it never executes entered CSS. */
const labControls = document.getElementById('box-lab-controls');
const labWidth = document.getElementById('lab-width');
const labPadding = document.getElementById('lab-padding');
const labSizing = document.getElementById('lab-sizing');
const labCard = document.getElementById('lab-card');

function updateBoxLab() {
    const width = Number(labWidth.value);
    const padding = Number(labPadding.value);
    const sizing = labSizing.value;
    labCard.style.width = `${width}px`;
    labCard.style.padding = `${padding}px`;
    labCard.style.boxSizing = sizing;
    document.getElementById('lab-width-value').textContent = `${width}px`;
    document.getElementById('lab-padding-value').textContent = `${padding}px`;
    const outerWidth = labCard.getBoundingClientRect().width;
    const contentWidth = outerWidth - 2 * padding - 4;
    document.getElementById('lab-measurement').textContent =
        `Measured outer width: ${outerWidth}px. Content width: ${contentWidth}px. ` +
        (sizing === 'content-box'
            ? `${width} + ${2 * padding} padding + 4 border = ${outerWidth}px.`
            : 'Padding and border fit inside the declared width.');
    document.getElementById('lab-css').textContent =
        `.sample {\n    width: ${width}px;\n    padding: ${padding}px;\n` +
        `    border: 2px solid;\n    box-sizing: ${sizing};\n}`;
}

labControls.addEventListener('input', updateBoxLab);
labControls.addEventListener('change', updateBoxLab);
labControls.addEventListener('submit', event => event.preventDefault());
labControls.addEventListener('reset', () => requestAnimationFrame(updateBoxLab));
updateBoxLab();
