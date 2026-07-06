import { apiFetch } from "./api.js";

export async function uploadDataset(file) {
    const formData = new FormData();
    formData.append("file", file);

    return apiFetch("/api/datasets/", { method: "POST", body: formData });
}

export function renderDatasetList(listElement, datasets) {
    listElement.innerHTML = "";
    for (const dataset of datasets) {
        const item = document.createElement("li");
        item.textContent = dataset.file;
        listElement.appendChild(item);
    }
}
