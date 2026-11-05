
const API_URL = "http://127.0.0.1:8000/api/demo-recommend";

async function getRecommendation() {

    const userInput = document.getElementById("userInput").value.trim();

    const button = document.getElementById("searchButton");
    const loading = document.getElementById("loading");
    const error = document.getElementById("error");
    const results = document.getElementById("results");

    if (userInput.length < 5) {
        error.textContent = "Please describe what product you are looking for.";
        error.classList.remove("hidden");
        return;
    }

    error.classList.add("hidden");
    results.classList.add("hidden");
    loading.classList.remove("hidden");

    button.disabled = true;
    button.textContent = "Researching...";

    try {

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_input: userInput
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        displayRecommendation(data);

    } catch (err) {

        error.textContent = err.message;
        error.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");
        button.disabled = false;
        button.textContent = "Find my product →";

    }
}


// Only allow absolute http(s) links (blocks javascript: and data: URLs).
function isSafeUrl(value) {
    try {
        const url = new URL(value);
        return url.protocol === "http:" || url.protocol === "https:";
    } catch {
        return false;
    }
}

function buildSourceLine(source) {

    const line = document.createElement("p");
    line.style.fontSize = "13px";
    line.style.color = "#8491a5";

    if (!source || source.type === "synthetic") {
        line.textContent =
            "Source: synthetic demo record (not a real listing)";
        return line;
    }

    line.append("Source: ");

    if (isSafeUrl(source.url)) {
        const link = document.createElement("a");
        link.href = source.url;
        link.textContent = source.name || "listing";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        line.appendChild(link);
    } else {
        line.append(source.name || "unknown");
    }

    if (source.fetched_at) {
        const when = new Date(source.fetched_at);
        if (!isNaN(when)) {
            line.append(` · fetched ${when.toLocaleString("en-IN")}`);
        }
    }

    return line;
}

function buildReviewLine(reviews) {

    const line = document.createElement("p");
    line.style.fontSize = "13px";

    const status = reviews?.status || "missing";

    if (status === "verified") {
        line.textContent =
            `Reviews: ${reviews.rating}/5 from ${reviews.count} ` +
            "reviews (verified source)";
    } else if (status === "unverified") {
        line.textContent =
            `Reviews: ${reviews.rating}/5 listed, but unverified`;
    } else {
        line.textContent = "Reviews: not available";
        line.style.color = "#8491a5";
    }

    return line;
}


function displayRecommendation(data) {

    const results = document.getElementById("results");
    const content = document.getElementById("recommendationContent");

    const recommendation =
        data.agents?.recommendation_agent;

    if (!recommendation || recommendation.status !== "success") {
        throw new Error("No recommendation could be generated.");
    }

    const winner = recommendation.best_overall_recommendation;
    const gaming = recommendation.gaming_alternative;

    content.replaceChildren();

    const card = document.createElement("div");
    card.className = "result-card";

    const heading = document.createElement("h3");
    heading.textContent = "🏆 Best Overall Recommendation";

    const name = document.createElement("p");
    name.textContent = winner.product_name;

    const price = document.createElement("p");
    price.textContent = `Price: ₹${winner.price_inr.toLocaleString("en-IN")}`;

    const score = document.createElement("p");
    score.textContent = `Overall Score: ${winner.overall_score}`;

    card.append(heading, name, price, score);

    const reasons = document.createElement("p");
    reasons.textContent =
        "Why recommended: " + winner.why_recommended.join(", ");

    card.appendChild(reasons);

    card.appendChild(buildSourceLine(winner.source));
    card.appendChild(buildReviewLine(winner.reviews));

    content.appendChild(card);

    if (gaming) {

        const gamingCard = document.createElement("div");
        gamingCard.className = "result-card";

        const gamingHeading = document.createElement("h3");
        gamingHeading.textContent = "🎮 Gaming Alternative";

        const gamingName = document.createElement("p");
        gamingName.textContent = `${gaming.brand} ${gaming.model}`;

        const gamingPrice = document.createElement("p");
        gamingPrice.textContent =
            `Price: ₹${gaming.price_inr.toLocaleString("en-IN")}`;

        gamingCard.append(
            gamingHeading,
            gamingName,
            gamingPrice
        );

        gamingCard.appendChild(buildReviewLine({
            status: gaming.review_status,
            rating: gaming.rating,
            count: gaming.review_count
        }));

        content.appendChild(gamingCard);
    }

    const disclaimer = document.createElement("p");
    disclaimer.textContent = recommendation.important_disclaimer;
    disclaimer.style.color = "#8491a5";
    disclaimer.style.fontSize = "12px";

    content.appendChild(disclaimer);

    results.classList.remove("hidden");
}
