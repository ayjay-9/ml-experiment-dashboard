import { uploadDataset, renderDatasetList } from "./datasets.js";
import { createExperiment, populateAlgorithmOptions } from "./experiments.js";

let currentDataset = null;
const uploadedDatasets = [];

const uploadForm = document.getElementById("upload-form");
const datasetFileInput = document.getElementById("dataset-file");
const datasetList = document.getElementById("dataset-list");
const experimentSection = document.getElementById("experiment-section");
const experimentForm = document.getElementById("experiment-form");
const targetColumnSelect = document.getElementById("target-column");
const taskTypeSelect = document.getElementById("task-type");
const algorithmSelect = document.getElementById("algorithm");
const resultsSection = document.getElementById("results-section");
const resultsStatus = document.getElementById("results-status");

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

    populateAlgorithmOptions(algorithmSelect, taskTypeSelect.value);
    experimentSection.hidden = false;
});

taskTypeSelect.addEventListener("change", () => {
    populateAlgorithmOptions(algorithmSelect, taskTypeSelect.value);
});

experimentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!currentDataset) return;

    const experiment = await createExperiment({
        dataset: currentDataset.id,
        target_column: targetColumnSelect.value,
        task_type: taskTypeSelect.value,
        algorithm: algorithmSelect.value,
        hyperparameters: {},
    });

    resultsSection.hidden = false;
    resultsStatus.textContent = `Status: ${experiment.status}`;
});

populateAlgorithmOptions(algorithmSelect, taskTypeSelect.value);
