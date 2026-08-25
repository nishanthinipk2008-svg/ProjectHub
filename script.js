// ================================
// PROJECTHUB DASHBOARD
// ================================

// Dashboard statistics
let totalProjects = 12;
let activeProjects = 7;
let completedProjects = 4;
let pendingTasks = 18;


// ================================
// LOAD DASHBOARD DATA
// ================================

async function loadDashboardData() {

    try {

        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Unable to load dashboard data");
        }

        const data = await response.json();

        totalProjects = data.totalProjects;
        activeProjects = data.activeProjects;
        completedProjects = data.completedProjects;
        pendingTasks = data.pendingTasks;

        updateDashboardNumbers();

    } catch (error) {

        console.log("Dashboard data not available:", error);

        // Keep original dashboard values if backend data
        // is not available.
        updateDashboardNumbers();

    }
}


// ================================
// UPDATE DASHBOARD NUMBERS
// ================================

function updateDashboardNumbers() {

    const statCards =
        document.querySelectorAll(".stat-card h2");

    if (statCards.length >= 4) {

        statCards[0].textContent = totalProjects;

        statCards[1].textContent = String(activeProjects).padStart(2, "0");

        statCards[2].textContent = String(completedProjects).padStart(2, "0");

        statCards[3].textContent = pendingTasks;

    }
}


// ================================
// ADD PROJECT BUTTON
// ================================

const addProjectButton =
    document.querySelector(".add-project-btn");

if (addProjectButton) {

    addProjectButton.addEventListener("click", function () {

        alert("New Project feature coming soon!");

    });

}


// ================================
// VIEW ALL BUTTON
// ================================

const viewButton =
    document.querySelector(".view-btn");

if (viewButton) {

    viewButton.addEventListener("click", function () {

        alert("Showing all projects...");

    });

}


// ================================
// START DASHBOARD
// ================================

loadDashboardData();