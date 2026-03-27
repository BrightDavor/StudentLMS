document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("lecturerForm");
    const nextBtns = document.querySelectorAll(".next-btn");
    const prevBtns = document.querySelectorAll(".prev-btn");
    const formSteps = document.querySelectorAll(".form-step");
    const progress = document.getElementById("progress");

    let formStepNum = 0;

    // Show the active step
    const updateFormSteps = () => {
        formSteps.forEach((step, index) => {
            step.classList.toggle("form-step-active", index === formStepNum);
        });
        updateProgressBar();
    };

    // Update progress bar
    const updateProgressBar = () => {
        const percent = ((formStepNum) / (formSteps.length - 1)) * 100;
        progress.style.width = `${percent}%`;
    };

    // Next button click
    nextBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            if (validateStep(formSteps[formStepNum])) {
                formStepNum++;
                updateFormSteps();
            }
        });
    });

    // Previous button click
    prevBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            formStepNum--;
            updateFormSteps();
        });
    });

    // Simple step validation
    const validateStep = (step) => {
        const inputs = step.querySelectorAll("input");
        for (let input of inputs) {
            if (!input.checkValidity()) {
                input.reportValidity();
                return false;
            }
        }
        return true;
    };

    updateFormSteps();
});
