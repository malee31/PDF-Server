const selectPDFInput = document.getElementById("select-pdf");
const uploadLabel = document.getElementById("pdf-upload-label");
const uploadPDFInput = document.getElementById("pdf-upload");
const pageRangeInput = document.getElementById("page-range");

selectPDFInput.addEventListener("change", e => {
	if(e.target.value === "Custom Upload") {
		console.log("Custom Upload Selected");
		uploadLabel.classList.remove("hidden");
		return;
	}
	uploadLabel.classList.add("hidden");
	console.log(`PDF Selected: ${e.target.value}`);
});

const allowedKeys = "1234567890 -,";
pageRangeInput.addEventListener("keypress", e => {
	if(allowedKeys.includes(e.key)) console.log("Allowed");
	else e.preventDefault();
	// TODO: Add a prompt saying that only specific characters are allowed
})