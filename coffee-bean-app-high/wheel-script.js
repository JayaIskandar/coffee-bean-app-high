const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const numSegments = drinks.length;
const angleSegment = 2 * Math.PI / numSegments;
const blinkDuration = 200; // Duration for each blink (in ms)
let radius; // Global variable for radius
const lightBrown = '#d2691e'; // Light brown color
const darkBrown = '#b05615';  // Dark brown color
const red = '#ff4500'; // Red color for highlighting

function resizeCanvas() {
    const container = document.querySelector('.wheel-container');
    const size = Math.min(container.offsetWidth, window.innerHeight * 0.7);
    canvas.width = size;
    canvas.height = size;
    drawWheel(0); // Initial draw with no highlight
}

function drawWheel(rotationAngle, highlightIndex = -1) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    radius = Math.min(centerX, centerY) - 10; // Set global radius

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(rotationAngle);
    
    // Draw wheel segments
    for (let i = 0; i < numSegments; i++) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, radius, i * angleSegment, (i + 1) * angleSegment);
        ctx.fillStyle = (i === highlightIndex) ? red : (i % 2 === 0 ? lightBrown : darkBrown); // Alternating colors with red for highlight
        ctx.fill();
        ctx.stroke();
        ctx.save();
        ctx.rotate(i * angleSegment + angleSegment / 2);
        ctx.fillStyle = 'white';
        ctx.font = `${radius * 0.06}px Arial`;
        ctx.fillText(drinks[i], radius * 0.3, 0);
        ctx.restore();
    }

    // Draw target line (if needed)
    ctx.restore();
}

let spinning = false;
function spinWheel() {
    if (spinning) return;
    spinning = true;

    const spins = Math.floor(Math.random() * 5 + 5);
    const duration = 2000; // Total duration of spin (in ms)
    const blinkCount = Math.floor(duration / blinkDuration); // Number of blinks
    let startTime;
    let blinkIndex = 0;
    const randomStartAngle = Math.random() * 360; // Random starting angle

    function animateSpin(time) {
        if (!startTime) startTime = time;
        const progress = time - startTime;
        const currentAngle = (progress / duration) * 360 + randomStartAngle; // Include random start angle

        drawWheel((currentAngle % 360) * Math.PI / 180, blinkIndex);

        if (progress < duration) {
            if (progress % blinkDuration < blinkDuration / 2) {
                // Blink effect: toggle highlight
                blinkIndex = Math.floor(((progress / blinkDuration) % numSegments));
            } else {
                blinkIndex = -1;
            }
            requestAnimationFrame(animateSpin);
        } else {
            // Determine the final slice based on the stopping angle
            const normalizedAngle = (currentAngle % 360);
            const resultIndex = Math.floor(((360 - normalizedAngle) / (360 / numSegments)) % numSegments);
            
            // Keep the final result highlighted
            drawWheel((currentAngle % 360) * Math.PI / 180, resultIndex);

            const resultElement = document.getElementById('result');
            resultElement.innerHTML = `<strong>You got:</strong> ${drinks[resultIndex]}<br><br><img src="${images[resultIndex]}" alt="${drinks[resultIndex]}" style="width: 300px; border-radius: 40px; max-width: 100%;"><br><br>${descriptions[resultIndex]}`;
            spinning = false;
        }
    }

    requestAnimationFrame(animateSpin);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
drawWheel(0); // Initial draw with no highlight
