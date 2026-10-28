
const tipButton = document.getElementById("tipButton");
const tipMessage = document.getElementById("tipMessage");

const studyTips = [
    "Study for 25 minutes, then take a 5-minute break.",
    "Practise one problem before reading the solution.",
    "Revise today's lessons before going to sleep.",
    "Start with your weakest topic and set one small goal.",
    "Keep your phone away during focused study time."
];

if (tipButton && tipMessage) {
    tipButton.addEventListener("click", function () {
        const randomIndex = Math.floor(Math.random() * studyTips.length);
        tipMessage.textContent = studyTips[randomIndex];
    });
}
