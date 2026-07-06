import { apiFetch } from "./api.js";

export async function createExperiment(payload) {
    return apiFetch("/api/experiments/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
}

export function populateAlgorithmOptions(selectElement, taskType) {
    const algorithmsByTaskType = {
        classification: ["logistic_regression", "random_forest_classifier", "svc"],
        regression: ["linear_regression", "random_forest_regressor", "svr"],
    };

    selectElement.innerHTML = "";
    for (const algorithm of algorithmsByTaskType[taskType]) {
        const option = document.createElement("option");
        option.value = algorithm;
        option.textContent = algorithm;
        selectElement.appendChild(option);
    }
}
