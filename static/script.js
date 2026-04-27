let locationDropdown;

// Load locations
fetch("/locations")
.then(res => res.json())
.then(data => {
    let dropdown = document.getElementById("location");

    data.locations.forEach(loc => {
        let option = document.createElement("option");
        option.value = loc;
        option.text = loc;
        dropdown.appendChild(option);
    });

    locationDropdown = new Choices(dropdown, {
        searchEnabled: true,
        itemSelectText: '',
        placeholderValue: 'Search location...'
    });
});

function predictPrice() {
    document.getElementById("result").innerText = "Calculating...";

    const data = {
        location: document.getElementById("location").value,
        sqft: document.getElementById("sqft").value,
        bath: document.getElementById("bath").value,
        bhk: document.getElementById("bhk").value
    };

    fetch("/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerHTML =
            "💰 Estimated Price: ₹ " + data.predicted_price + " Lakhs<br><br>" +
            "🧠 " + data.explanation;
    });
}