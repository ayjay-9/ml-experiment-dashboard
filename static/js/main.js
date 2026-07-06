import { uploadDataset, renderDatasetList } from "./datasets.js";

let currentDataset = null;
const uploadedDatasets = [];

const uploadForm = document.getElementById("upload-form");
const datasetFileInput = document.getElementById("dataset-file");
const datasetList = document.getElementById("dataset-list");
const experimentSection = document.getElementById("experiment-section");
const targetColumnSelect = document.getElementById("target-column");

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = datasetFileInput.files[0];
    if (!file) return;

    currentDataset = await uploadDataset(file);
    uploadedDatasets.push(currentDataset);
    renderDatasetList(datasetList, uploadedDatasets);

    targetColumnSelect.innerHTML = "";
    for (const column of currentDataset.column_names) {
        const option = document.createElement("option");
        option.value = column;
        option.textContent = column;
        targetColumnSelect.appendChild(option);
    }

    experimentSection.hidden = false;
});
