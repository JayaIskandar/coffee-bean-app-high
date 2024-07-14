const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const numSegments = drinks.length;
const angleSegment = 2 * Math.PI / numSegments;

function resizeCanvas() {
    const container = document.querySelector('.wheel-container');
    const size = Math.min(container.offsetWidth, window.innerHeight * 0.7);
    canvas.width = size;
    canvas.height = size;
    drawWheel(0);
}

function drawWheel(rotationAngle) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(rotationAngle);
    
    for (let i = 0; i < numSegments; i++) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, radius, i * angleSegment, (i + 1) * angleSegment);
        ctx.fillStyle = i % 2 === 0 ? '#d2691e' : '#f5deb3';
        ctx.fill();
        ctx.stroke();
        ctx.save();
        ctx.rotate(i * angleSegment + angleSegment / 2);
        ctx.fillStyle = 'white';
        ctx.font = `${radius * 0.06}px Arial`;
        ctx.fillText(drinks[i], radius * 0.3, 0);
        ctx.restore();
    }
    ctx.restore();
}

let spinning = false;
function spinWheel() {
    if (spinning) return;
    spinning = true;
    const spins = Math.floor(Math.random() * 5 + 5);
    const finalAngle = Math.random() * 360;
    const totalAngle = (spins * 360) + finalAngle;
    const duration = 8000;
    let startTime;

    function animateSpin(time) {
        if (!startTime) startTime = time;
        const progress = time - startTime;
        const currentAngle = (totalAngle * (progress / duration)) % 360;
        drawWheel(currentAngle * Math.PI / 180);
        if (progress < duration) {
            requestAnimationFrame(animateSpin);
        } else {
            const resultIndex = Math.floor((finalAngle / (360 / numSegments)) % numSegments);
            const resultElement = document.getElementById('result');
            resultElement.innerHTML = `<strong>You got:</strong> ${drinks[resultIndex]}<br><br>${descriptions[resultIndex]}`;
            spinning = false;
        }
    }

    requestAnimationFrame(animateSpin);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();
drawWheel(0);