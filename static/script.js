function submitForm(event) {
    event.preventDefault(); // Prevent form submission

    const form = document.getElementById("questionnaire-form");
    const selects = form.querySelectorAll("select");

    const parameters = {}; // Holds the sum of chosen parameters
    const maxParameters = {}; // Holds the sum of maximum allowed values for each parameter

    // Iterate through all the select elements
    selects.forEach(select => {
        const dataPoints = select.selectedOptions[0].dataset.points.split(",").map(Number); // Get selected option points
        const preference = select.dataset.preference.split(","); // Get preferences

        preference.forEach((param, index) => {
            // Add chosen points to the parameter
            parameters[param] = (parameters[param] || 0) + (dataPoints[index] || 0);

            // Add max points to the parameter
            const maxPoints = select.dataset.points.split(",").map(Number);
            maxParameters[param] = (maxParameters[param] || 0) + Math.max(...maxPoints);
        });
    });

    // Send the data to the backend
    fetch("/submit-answers/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: JSON.stringify({
            parameters: parameters,
            maxParameters: maxParameters
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        console.log("Server response:", data);
    })
    .catch(error => {
        console.error("Error submitting form:", error);
    });
}
