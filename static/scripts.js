const selectPDFInput = document.getElementById("select-pdf");
const uploadLabel = document.getElementById("pdf-upload-label");
const uploadPDFInput = document.getElementById("pdf-upload");
const pageRangeInput = document.getElementById("page-range");
const form = document.getElementById("clip");

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
})

const allowedKeys = "1234567890-,";
pageRangeInput.addEventListener("keypress", e => {
	if(allowedKeys.includes(e.key)) console.log("Allowed");
	else e.preventDefault();
	// TODO: Add a prompt saying that only specific characters are allowed
});

form.addEventListener("submit", e => {
	e.preventDefault();
	const data = new FormData();
	// TODO: Check if inputs are filled
	if(selectPDFInput.value === "Custom Upload") data.append("uploadedPDF", uploadPDFInput.files[0]);
	else data.append("selectedPDF", selectPDFInput.value);
	data.append("pageRange", pageRangeInput.value);

	const req = new XMLHttpRequest();
	req.addEventListener("load", () => {
		if(req.status === 200) {
			console.log("Success!");
			window.location.href = req.responseText;
		} else console.warn(`Irregular Status: ${req.statusText}`);
	});
	req.addEventListener("error", console.error);
	req.open("POST", `${window.location.origin}/submit`, true);
	req.send(data);
});