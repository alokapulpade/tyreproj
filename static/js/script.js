
// ================================
// SIDE MENU
// ================================

const menuBtn = document.getElementById("menuBtn");
const closeBtn = document.getElementById("closeBtn");
const sideMenu = document.getElementById("sideMenu");

if (menuBtn && sideMenu) {
    menuBtn.addEventListener("click", function () {
        sideMenu.classList.add("open");
    });
}

if (closeBtn && sideMenu) {
    closeBtn.addEventListener("click", function () {
        sideMenu.classList.remove("open");
    });
}


// ================================
// TYRE MODAL
// ================================

function showTyre(
    id,
    brand,
    model,
    size,
    position,
    availability,
    price,
    image
) {

    const modal = document.getElementById("tyreModal");

    if (!modal) return;

    const modalBrand = document.getElementById("modalBrand");
    const modalModel = document.getElementById("modalModel");
    const modalSize = document.getElementById("modalSize");
    const modalPosition = document.getElementById("modalPosition");
    const modalAvailability = document.getElementById("modalAvailability");
    const modalPrice = document.getElementById("modalPrice");

    if (modalBrand) {
        modalBrand.innerText = brand;
    }

    if (modalModel) {
        modalModel.innerText = model;
    }

    if (modalSize) {
        modalSize.innerText = size;
    }

    if (modalPosition) {
        modalPosition.innerText = position;
    }

    if (modalAvailability) {
        modalAvailability.innerText = availability;
    }

    if (modalPrice) {
        modalPrice.innerText = price;
    }


    // Tyre image

    const imageBox = document.getElementById("modalImage");

    if (imageBox) {

        if (image) {

            imageBox.innerHTML = `
                <img
                    src="/static/images/${image}"
                    alt="${brand} ${model}"
                    onerror="this.style.display='none'"
                >
            `;

        } else {

            imageBox.innerHTML = `
                <div class="fake-tyre">🛞</div>
            `;

        }
    }


    // WhatsApp button

    const whatsappButton =
        document.getElementById("whatsappButton");

    if (whatsappButton) {

        whatsappButton.href =
            `/whatsapp/${id}`;

    }


    // Favourite button

    const favouriteButton =
        document.getElementById("favouriteButton");

    if (favouriteButton) {

        favouriteButton.href =
            `/favourite/${id}`;

    }


    // Open modal

    modal.style.display = "flex";
}


// Close tyre modal

function closeTyre() {

    const modal =
        document.getElementById("tyreModal");

    if (modal) {

        modal.style.display = "none";

    }
}


// Close modal when clicking outside it

window.addEventListener("click", function (event) {

    const modal =
        document.getElementById("tyreModal");

    if (modal && event.target === modal) {

        closeTyre();

    }

});


// ================================
// GEMINI CHATBOT
// ================================

const chatbotBtn =
    document.getElementById("chatbotBtn");

const chatbotBox =
    document.getElementById("chatbotBox");

const chatbotClose =
    document.getElementById("chatbotClose");

const chatbotInput =
    document.getElementById("chatbotInput");

const chatbotSend =
    document.getElementById("chatbotSend");

const chatbotMessages =
    document.getElementById("chatbotMessages");


// Open / close chatbot

if (chatbotBtn && chatbotBox) {

    chatbotBtn.addEventListener("click", function () {

        chatbotBox.classList.toggle("open");

        if (
            chatbotBox.classList.contains("open") &&
            chatbotInput
        ) {

            chatbotInput.focus();

        }

    });

}


// Close chatbot

if (chatbotClose && chatbotBox) {

    chatbotClose.addEventListener("click", function () {

        chatbotBox.classList.remove("open");

    });

}


// Add chatbot message

function addMessage(message, type) {

    if (!chatbotMessages) return;

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(
        type === "user"
            ? "user-message"
            : "bot-message"
    );

    messageDiv.textContent = message;

    chatbotMessages.appendChild(messageDiv);

    chatbotMessages.scrollTop =
        chatbotMessages.scrollHeight;
}


// Send message to Gemini

function sendMessage() {

    if (!chatbotInput) return;

    const message =
        chatbotInput.value.trim();

    if (message === "") {
        return;
    }


    // Show user's message

    addMessage(message, "user");

    chatbotInput.value = "";


    // Send to Flask / Gemini

    fetch("/api/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    })

    .then(response => {

        if (!response.ok) {
            throw new Error("Chatbot request failed");
        }

        return response.json();

    })

    .then(data => {

        addMessage(
            data.reply || "Sorry, I couldn't understand that.",
            "bot"
        );

    })

    .catch(error => {

        console.error(
            "Chatbot error:",
            error
        );

        addMessage(
            "Sorry, I can't help you with that request right now.",
            "bot"
        );

    });

}


// Send button

if (chatbotSend) {

    chatbotSend.addEventListener(
        "click",
        sendMessage
    );

}


// Press Enter to send

if (chatbotInput) {

    chatbotInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}

// ================================
// SEARCH BY TYRE
// ================================

const openTyreSearch =
    document.getElementById("openTyreSearch");

const tyreSearchModal =
    document.getElementById("tyreSearchModal");

const closeTyreSearch =
    document.getElementById("closeTyreSearch");

const tyreSearchInput =
    document.getElementById("tyreSearchInput");

const tyreSearchButton =
    document.getElementById("tyreSearchButton");

const tyreSearchResults =
    document.getElementById("tyreSearchResults");


// Open tyre search

if (openTyreSearch && tyreSearchModal) {
    openTyreSearch.addEventListener("click", function () {

        tyreSearchModal.classList.add("open");
        tyreSearchModal.style.display = "flex";

        if (tyreSearchInput) {
            tyreSearchInput.focus();
        }
    });
}


// Close tyre search

if (closeTyreSearch && tyreSearchModal) {
    closeTyreSearch.addEventListener("click", function () {

        tyreSearchModal.classList.remove("open");
        tyreSearchModal.style.display = "none";

        if (tyreSearchResults) {
            tyreSearchResults.innerHTML = "";
        }

        if (tyreSearchInput) {
            tyreSearchInput.value = "";
        }
    });
}


// Perform tyre search

function performTyreSearch() {

    if (!tyreSearchInput || !tyreSearchResults) {
        return;
    }

    const size =
        tyreSearchInput.value.trim();

    if (size === "") {

        tyreSearchResults.innerHTML = `
            <div class="search-results-placeholder">
                <div class="placeholder-icon">🔎</div>
                <h3>Enter a Tyre Size</h3>
                <p>Please enter a tyre size such as 195/65 R15.</p>
            </div>
        `;

        return;
    }


    // Loading state

    tyreSearchResults.innerHTML = `
        <div class="search-loading">
            <div class="search-spinner"></div>
            <p>Searching our tyre catalogue...</p>
        </div>
    `;


    fetch(
        `/api/search-tyre?size=${encodeURIComponent(size)}`
    )

    .then(response => {

        if (!response.ok) {
            throw new Error("Search request failed");
        }

        return response.json();

    })

    .then(results => {

        if (!results || results.length === 0) {

            tyreSearchResults.innerHTML = `
                <div class="search-results-placeholder">
                    <div class="placeholder-icon">😕</div>
                    <h3>No Matching Tyres</h3>
                    <p>
                        We couldn't find a tyre matching
                        <strong>${escapeHtml(size)}</strong>.
                    </p>
                    <span>
                        Try another size such as 195/65 R15.
                    </span>
                </div>
            `;

            return;
        }


        let html = `
            <div class="search-results-heading">
                <div>
                    <p class="small-title">MATCHING TYRES</p>
                    <h3>${results.length} tyre${results.length > 1 ? "s" : ""} found</h3>
                </div>
            </div>

            <div class="search-result-grid">
        `;


        results.forEach(tyre => {

    const imageHtml = tyre.image
        ? `
            <img
                src="/static/images/${escapeHtml(tyre.image)}"
                alt="${escapeHtml(tyre.brand)} ${escapeHtml(tyre.model)}"
                onerror="this.style.display='none'"
            >
          `
        : `
            <div class="fake-tyre">🛞</div>
          `;

    const availabilityClass =
        tyre.availability === "Available"
            ? "available"
            : "unavailable";

    html += `
        <div class="search-result-card">

            <div class="search-result-image">
                ${imageHtml}
            </div>

            <div class="search-result-info">

                <div class="brand">
                    ${escapeHtml(tyre.brand)}
                </div>

                <h3>
                    ${escapeHtml(tyre.model)}
                </h3>

                <p>
                    <strong>Size:</strong>
                    ${escapeHtml(tyre.size)}
                </p>

                <p>
                    <strong>Position:</strong>
                    ${escapeHtml(tyre.position)}
                </p>

                <span class="${availabilityClass}">
                    ${escapeHtml(tyre.availability)}
                </span>

                <div class="search-result-bottom">

                    <strong class="search-result-price">
                        ₹${escapeHtml(String(tyre.price))}
                    </strong>

                    <button
                        type="button"
                        class="search-view-btn"
                        data-tyre-id="${tyre.id}"
                    >
                        View Details
                    </button>

                </div>

            </div>

        </div>
    `;
});

html += `</div>`;

tyreSearchResults.innerHTML = html;


// Attach click events AFTER the results are created

const viewButtons =
    tyreSearchResults.querySelectorAll(".search-view-btn");

viewButtons.forEach((button, index) => {

    button.addEventListener("click", function (event) {

        event.preventDefault();
        event.stopPropagation();

        const tyre = results[index];

        if (!tyre) {
            return;
        }

        openSearchTyreDetails(
            tyre.id,
            tyre.brand,
            tyre.model,
            tyre.size,
            tyre.position,
            tyre.availability,
            tyre.price,
            tyre.image || ""
        );

    });

});


    })

    .catch(error => {

        console.error(
            "Tyre search error:",
            error
        );

        tyreSearchResults.innerHTML = `
            <div class="search-results-placeholder">
                <div class="placeholder-icon">⚠️</div>
                <h3>Something Went Wrong</h3>
                <p>
                    We couldn't search the tyre catalogue right now.
                </p>
            </div>
        `;

    });

}


// Search button

if (tyreSearchButton) {

    tyreSearchButton.addEventListener(
        "click",
        performTyreSearch
    );

}


// Press Enter to search

if (tyreSearchInput) {

    tyreSearchInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                performTyreSearch();

            }

        }
    );

}


// Open existing tyre details modal from search results

function openSearchTyreDetails(
    id,
    brand,
    model,
    size,
    position,
    availability,
    price,
    image
) {
    // Close the tyre search popup
    const searchModal = document.getElementById("tyreSearchModal");

    if (searchModal) {
        searchModal.classList.remove("open");
        searchModal.style.display = "none";
    }

    // Open the actual tyre details popup
    showTyre(
        id,
        brand,
        model,
        size,
        position,
        availability,
        price,
        image
    );

    // Make absolutely sure the details popup is above everything
    const tyreModal = document.getElementById("tyreModal");

    if (tyreModal) {
        tyreModal.style.display = "flex";
        tyreModal.style.zIndex = "100001";
    }
}


// Escape HTML

function escapeHtml(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


// Escape JavaScript strings

function escapeJs(value) {

    return String(value)
        .replace(/\\/g, "\\\\")
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\r/g, "\\r")
        .replace(/\n/g, "\\n");

}



// ================================
// SEARCH BY VEHICLE
// ================================

const openVehicleSearch =
    document.getElementById("openVehicleSearch");

const vehicleSearchModal =
    document.getElementById("vehicleSearchModal");

const closeVehicleSearch =
    document.getElementById("closeVehicleSearch");

const vehicleSearchButton =
    document.getElementById("vehicleSearchButton");


// Open vehicle search

if (openVehicleSearch && vehicleSearchModal) {

    openVehicleSearch.addEventListener("click", function () {

        vehicleSearchModal.classList.add("open");

    });

}


// Close vehicle search

if (closeVehicleSearch && vehicleSearchModal) {

    closeVehicleSearch.addEventListener("click", function () {

        vehicleSearchModal.classList.remove("open");

    });

}


// Vehicle search placeholder

if (vehicleSearchButton) {

    vehicleSearchButton.addEventListener("click", function () {

        const results =
            document.getElementById("vehicleSearchResults");

        if (!results) return;

        results.innerHTML = `
            <div class="search-results-placeholder">
                <div class="placeholder-icon">🚗</div>
                <h3>Vehicle Search Coming Soon</h3>
                <p>
                    Vehicle model data is being added to our database.
                    Once it is available, you will be able to select
                    your vehicle and find compatible tyres here.
                </p>
            </div>
        `;

    });

}



// ================================
// CLOSE SEARCH MODALS
// ================================

window.addEventListener("click", function (event) {

    // Close tyre search
    if (
        tyreSearchModal &&
        event.target === tyreSearchModal
    ) {
        tyreSearchModal.classList.remove("open");
        tyreSearchModal.style.display = "none";

        if (tyreSearchResults) {
            tyreSearchResults.innerHTML = "";
        }

        if (tyreSearchInput) {
            tyreSearchInput.value = "";
        }
    }

    // Close vehicle search
    if (
        vehicleSearchModal &&
        event.target === vehicleSearchModal
    ) {
        vehicleSearchModal.classList.remove("open");
        vehicleSearchModal.style.display = "none";
    }
});


// Escape key closes search popups

window.addEventListener("keydown", function (event) {

    if (event.key !== "Escape") {
        return;
    }

    if (tyreSearchModal) {
        tyreSearchModal.classList.remove("open");
        tyreSearchModal.style.display = "none";

        if (tyreSearchResults) {
            tyreSearchResults.innerHTML = "";
        }

        if (tyreSearchInput) {
            tyreSearchInput.value = "";
        }
    }

    if (vehicleSearchModal) {
        vehicleSearchModal.classList.remove("open");
        vehicleSearchModal.style.display = "none";
    }
});