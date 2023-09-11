const form = document.getElementById("clip");

form.addEventListener("submit", e => {
	e.preventDefault();
	const data = new FormData(form);

	fetch(`${window.location.origin}/merge/submit`, {
		method: "POST",
		body: data
	}).then(res => {
		console.log(res)
		if(res.status === 200) {
			res.text().then(text => console.log(text))
		} else if(res.status === 202) {
			res.text().then(text => window.location = text)
		} else {
			console.warn(`Irregular Status: ${res.statusText}`)
		}
	}).catch(err => {
		displayError(`Error ${err.status}`, res.statusText);
	});
});