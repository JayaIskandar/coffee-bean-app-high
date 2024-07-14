const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const numSegments = drinks.length;
const angleSegment = 2 * Math.PI / numSegments;

function drawWheel(rotationAngle) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(300, 300);  // Center of the wheel
    ctx.rotate(rotationAngle);
    for (let i = 0; i < numSegments; i++) {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, 250, i * angleSegment, (i + 1) * angleSegment);
        ctx.fillStyle = i % 2 === 0 ? '#d2691e' : '#f5deb3';  // Old brown and light brown
        ctx.fill();
        ctx.stroke();
        ctx.save();
        ctx.rotate(i * angleSegment + angleSegment / 2);
        ctx.fillStyle = 'white';
        ctx.fillText(drinks[i], 70, 0);
        ctx.restore();
    }
    ctx.restore();
}

let spinning = false;
function spinWheel() {
    if (spinning) return;
    spinning = true;
    const spins = Math.floor(Math.random() * 5 + 5); // Fewer random spins
    const finalAngle = Math.random() * 360; // Random final angle
    const totalAngle = (spins * 360) + finalAngle;
    const duration = 8000; // Slower spin duration
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
            document.getElementById('result').innerText = 'You got: ' + drinks[resultIndex] + '\n' + descriptions[resultIndex];
            spinning = false;
        }
    }

    requestAnimationFrame(animateSpin);
}

drawWheel(0);