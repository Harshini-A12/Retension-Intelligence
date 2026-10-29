// ============================================================
// CONFIGURATION
// ============================================================

// API endpoint URL (Flask backend running on localhost port 5000)
const API_URL = "http://127.0.0.1:5000";

// ============================================================
// GET REFERENCES TO HTML ELEMENTS
// ============================================================

// Button and input elements
const predictBtn = document.getElementById("predictBtn");
const customerIdInput = document.getElementById("customerId");

// Status elements
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");

// Section elements
const resultSection = document.getElementById("resultSection");
const emptyState = document.getElementById("emptyState");

// ============================================================
// EVENT LISTENERS
// ============================================================

// When user clicks "ANALYZE CUSTOMER" button
predictBtn.addEventListener("click", analyzeCustomer);

// When user presses Enter key in the input field
customerIdInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        analyzeCustomer();
    }
});

// ============================================================
// MAIN FUNCTION: Analyze Customer
// ============================================================

async function analyzeCustomer() {
    
    // Get the customer ID from input field and remove extra spaces
    const customerId = customerIdInput.value.trim();

    // Validate: Check if customer ID is empty
    if (customerId === "") {
        showError("Please enter a customer ID.");
        return;
    }

    // --------------------------------------------------------
    // STEP 1: Prepare UI for loading
    // --------------------------------------------------------
    
    hideError();                              // Hide any previous error messages
    emptyState.classList.add("hidden");       // Hide the empty state
    resultSection.classList.add("hidden");    // Hide previous results
    loading.classList.remove("hidden");       // Show loading spinner
    predictBtn.disabled = true;               // Disable button to prevent multiple clicks

    try {
        
        // --------------------------------------------------------
        // STEP 2: Send request to backend API
        // --------------------------------------------------------
        
        const response = await fetch(
            `${API_URL}/predict`,              // API endpoint
            {
                method: "POST",                // HTTP POST method
                headers: {
                    "Content-Type": "application/json"  // Tell server we're sending JSON
                },
                body: JSON.stringify({         // Convert data to JSON string
                    customerID: customerId
                })
            }
        );

        // --------------------------------------------------------
        // STEP 3: Parse the response from backend
        // --------------------------------------------------------
        
        const data = await response.json();    // Convert response to JavaScript object

        // Check if request was successful
        if (!response.ok) {
            // If not successful, throw error with message from backend
            throw new Error(data.error || "Unable to analyze customer.");
        }

        // --------------------------------------------------------
        // STEP 4: Display the results
        // --------------------------------------------------------
        
        displayResult(data);

    } catch (error) {
        
        // --------------------------------------------------------
        // STEP 5: Handle any errors
        // --------------------------------------------------------
        
        console.error(error);                  // Log error to browser console
        showError(error.message);              // Show error message to user

    } finally {
        
        // --------------------------------------------------------
        // STEP 6: Clean up UI (runs whether success or error)
        // --------------------------------------------------------
        
        loading.classList.add("hidden");       // Hide loading spinner
        predictBtn.disabled = false;           // Re-enable button

    }
}

// ============================================================
// FUNCTION: Display Prediction Results
// ============================================================

function displayResult(data) {

    // Show results section and hide empty state
    resultSection.classList.remove("hidden");
    emptyState.classList.add("hidden");

    // --------------------------------------------------------
    // UPDATE CUSTOMER ID
    // --------------------------------------------------------
    
    document.getElementById("resultCustomerId").textContent = 
        data.customerID || "Unknown";

    // --------------------------------------------------------
    // UPDATE PREDICTION BADGE (High Risk or Likely to Stay)
    // --------------------------------------------------------
    
    const predictionBadge = document.getElementById("predictionBadge");
    const prediction = data.prediction || "";

    if (prediction.toLowerCase().includes("churn")) {
        // Customer is at high risk of churning
        predictionBadge.textContent = "HIGH CHURN RISK";
        predictionBadge.className = "prediction-badge churn";  // Red styling
    } else {
        // Customer is likely to stay
        predictionBadge.textContent = "LIKELY TO STAY";
        predictionBadge.className = "prediction-badge stay";   // Green styling
    }

    // --------------------------------------------------------
    // UPDATE CHURN PROBABILITY
    // --------------------------------------------------------
    
    // Convert probability from decimal (0.0-1.0) to percentage (0-100)
    const probability = Number(data.churn_probability || 0);
    const probabilityPercent = probability * 100;

    // Update probability text (e.g., "65.3%")
    document.getElementById("probability").textContent = 
        probabilityPercent.toFixed(1) + "%";

    // Update progress bar width
    document.getElementById("probabilityBar").style.width = 
        probabilityPercent + "%";

    // --------------------------------------------------------
    // UPDATE TOP METRICS
    // --------------------------------------------------------
    
    // Tenure (months with company)
    document.getElementById("tenure").textContent = 
        data.tenure ?? "—";

    // Monthly charges (billing amount)
    document.getElementById("monthlyCharges").textContent = 
        Number(data.MonthlyCharges || 0).toFixed(2);

    // Contract type (Month-to-month, One year, Two year)
    document.getElementById("contract").textContent = 
        data.Contract || "—";

    // --------------------------------------------------------
    // UPDATE CUSTOMER PROFILE DETAILS
    // --------------------------------------------------------
    
    // Gender
    document.getElementById("gender").textContent = 
        data.gender || "—";

    // Senior Citizen (convert 0/1 to Yes/No)
    document.getElementById("seniorCitizen").textContent = 
        Number(data.SeniorCitizen) === 1 ? "Yes" : "No";

    // Partner status
    document.getElementById("partner").textContent = 
        data.Partner || "—";

    // Dependents status
    document.getElementById("dependents").textContent = 
        data.Dependents || "—";

    // Internet service type
    document.getElementById("internetService").textContent = 
        data.InternetService || "—";

    // Payment method
    document.getElementById("paymentMethod").textContent = 
        data.PaymentMethod || "—";

    // --------------------------------------------------------
    // UPDATE AI RETENTION INSIGHT
    // --------------------------------------------------------
    
    const insightTitle = document.getElementById("insightTitle");
    const insightText = document.getElementById("insightText");
    const insightIcon = document.getElementById("insightIcon");

    if (probability >= 0.5) {
        
        // HIGH RISK: Customer needs attention
        
        insightTitle.textContent = "Customer needs attention";
        
        insightText.textContent = 
            "The model identifies a higher likelihood of churn. Consider reviewing this customer's contract, tenure, charges and subscribed services.";
        
        insightIcon.textContent = "!";  // Warning icon
        
        // Red/warning styling
        insightIcon.style.background = 
            "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)";
        insightIcon.style.color = "#991b1b";
        insightIcon.style.boxShadow = 
            "0 4px 12px rgba(239, 68, 68, 0.2)";

    } else {
        
        // LOW RISK: Customer appears stable
        
        insightTitle.textContent = "Customer appears stable";
        
        insightText.textContent = 
            "The model currently estimates a lower likelihood of churn based on the customer's profile and service information.";
        
        insightIcon.textContent = "✓";  // Checkmark icon
        
        // Green/success styling
        insightIcon.style.background = 
            "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)";
        insightIcon.style.color = "#065f46";
        insightIcon.style.boxShadow = 
            "0 4px 12px rgba(16, 185, 129, 0.2)";
    }

    // --------------------------------------------------------
    // UPDATE SUBSCRIBED SERVICES LIST
    // --------------------------------------------------------
    
    const servicesContainer = document.getElementById("services");
    
    // Clear previous services
    servicesContainer.innerHTML = "";

    // Array of service names and their values
    const services = [
        ["Phone Service", data.PhoneService],
        ["Multiple Lines", data.MultipleLines],
        ["Online Security", data.OnlineSecurity],
        ["Online Backup", data.OnlineBackup],
        ["Device Protection", data.DeviceProtection],
        ["Tech Support", data.TechSupport],
        ["Streaming TV", data.StreamingTV],
        ["Streaming Movies", data.StreamingMovies]
    ];

    // Loop through each service and create HTML element
    services.forEach(function(service) {
        
        const div = document.createElement("div");  // Create new div element
        div.className = "service";                  // Add CSS class
        div.textContent = service[0] + ": " + service[1];  // Set text
        
        // If service is active (Yes), add special styling
        if (service[1] === "Yes") {
            div.classList.add("active");
        }
        
        // Add the service div to the container
        servicesContainer.appendChild(div);
    });

    // --------------------------------------------------------
    // SMOOTH SCROLL TO RESULTS
    // --------------------------------------------------------
    
    setTimeout(function() {
        resultSection.scrollIntoView({
            behavior: "smooth",   // Smooth scrolling animation
            block: "start"        // Align to top of viewport
        });
    }, 100);  // Small delay for better UX
}

// ============================================================
// HELPER FUNCTION: Show Error Message
// ============================================================

function showError(message) {
    errorBox.textContent = message;           // Set error text
    errorBox.classList.remove("hidden");      // Make error box visible
}

// ============================================================
// HELPER FUNCTION: Hide Error Message
// ============================================================

function hideError() {
    errorBox.classList.add("hidden");         // Hide error box
}
