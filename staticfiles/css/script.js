const steps = Array.from(document.querySelectorAll(".form-step"));
const nextBtns = document.querySelectorAll(".next-btn");
const prevBtns = document.querySelectorAll(".prev-btn");
const progress = document.getElementById("progress");
let currentStep = 0;

nextBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        if (!validateStep(currentStep)) return;
        steps[currentStep].classList.remove("form-step-active");
        currentStep++;
        steps[currentStep].classList.add("form-step-active");
        updateProgress();
    });
});

prevBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        steps[currentStep].classList.remove("form-step-active");
        currentStep--;
        steps[currentStep].classList.add("form-step-active");
        updateProgress();
    });
});

function updateProgress() {
    const progressPercentage = ((currentStep + 1) / steps.length) * 100;
    progress.style.width = `${progressPercentage}%`;
}

function validateStep(step) {
    const inputs = steps[step].querySelectorAll("input");
    for (let input of inputs) {
        if (!input.value) {
            alert("Please fill in all fields");
            return false;
        }
    }
    return true;
}
