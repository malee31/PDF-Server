const selectPDFInput = document.getElementById("select-pdf");
const uploadLabel = document.getElementById("pdf-upload-label");
const uploadPDFInput = document.getElementById("pdf-upload");
const pageRangeInput = document.getElementById("page-range");
const form = document.getElementById("clip");

const errorBox = document.getElementById("error-box");
const errorTitle = document.getElementById("error-box-title");
const errorText = document.getElementById("error-box-text");
document.getElementById("error-box-dismiss").addEventListener("click", () => {
	errorBox.style.display = "none";
});

const successModal = document.getElementById("success-modal");
document.getElementById("success-modal-view").addEventListener("click", () => {
	if(successModal.dataset.targetFilename) window.location.href = `/view/${successModal.dataset.targetFilename}`;
});
document.getElementById("success-modal-download").addEventListener("click", () => {
	if(successModal.dataset.targetFilename) window.location.href = `/download/${successModal.dataset.targetFilename}`;
	successModal.style.display = "none";
});

selectPDFInput.addEventListener("change", e => {
	if(e.target.value === "Custom Upload") {
		console.log("Custom Upload Selected");
		uploadLabel.classList.remove("hidden");
		return;
	}
	uploadLabel.classList.add("hidden");
	console.log(`PDF Selected: ${e.target.value}`);
});

uploadPDFInput.addEventListener("change", e => {
	const files = e.target.files;
	const uploadText = document.getElementById("upload-text")
	if(files.length > 0 && files[0].name) uploadText.innerText = files[0].name;
	else uploadText.innerText = "Upload a PDF";
});

const allowedKeys = "1234567890-,";
pageRangeInput.addEventListener("keypress", e => {
	if(allowedKeys.includes(e.key)) console.log("Allowed");
	else e.preventDefault();
	// TODO: Add a prompt saying that only specific characters are allowed
});

function displayError(title, message) {
	errorBox.style.display = "";
	errorTitle.innerText = title;
	errorText.innerText = message;
	// console.error(message);
}

function createSuccessModal(targetFilename) {
	successModal.dataset.targetFilename = targetFilename;
	successModal.style.display = "";
}

form.addEventListener("submit", e => {
	e.preventDefault();
	const data = new FormData();
	// TODO: Check if inputs are filled
	if(selectPDFInput.value === "Custom Upload") {
		if(uploadPDFInput.files.length === 0) {
			displayError("No File Uploaded", "Attach a PDF and resubmit to continue");
			return;
		}
		data.append("uploadedPDF", uploadPDFInput.files[0]);
	} else data.append("selectedPDF", selectPDFInput.value);
	const range = pageRangeInput.value.replace(/[^0-9,-]/g, "");
	if(range.length === 0) {
		displayError("Invalid Page Range", "Enter a page range in the form of comma-separated numbers or number ranges\n(Example: 1,3-5,10)");
		return;
	}
	data.append("pageRange", pageRangeInput.value.replace(/[^0-9,-]/g, ""));

	const req = new XMLHttpRequest();
	req.addEventListener("load", () => {
		if(req.status === 200) {
			console.log(`Success! Filepath ${req.responseText}`);
			createSuccessModal(req.responseText);
		} else console.warn(`Irregular Status: ${req.statusText}`);
	});
	req.addEventListener("error", err => {
		console.error(err);
		displayError(`Error ${err.status}`, req.statusText);
	});
	req.open("POST", `${window.location.origin}/submit`, true);
	req.send(data);
});