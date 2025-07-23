<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bacterial Run and Tumble Motion</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f0f23, #1a1a3a);
            color: white;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }
        
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }
        
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
        }
        
        .description {
            font-size: 14px;
            margin-bottom: 20px;
            text-align: center;
            opacity: 0.8;
            max-width: 600px;
        }
        
        canvas {
            border: 2px solid #333;
            border-radius: 10px;
            background: radial-gradient(circle at center, #001122, #000000);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        
        .controls {
            margin-top: 15px;
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        button {
            padding: 8px 16px;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            border: none;
            border-radius: 5px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: scale(1.05);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .legend {
            margin-top: 15px;
            display: flex;
            gap: 20px;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">Bacterial Run and Tumble Motion</h1>
        <p class="description">
            Watch a single bacterium navigate toward food using run and tumble motion. 
            It leaves a red trail as it alternates between straight runs and random tumbles until reaching the food source.
        </p>
        
        <canvas id="canvas" width="800" height="500"></canvas>
        
        <div class="controls">
            <button id="startBtn" onclick="startSimulation()">Start</button>
            <button onclick="resetSimulation()">Reset</button>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #4444ff;"></div>
                <span>Bacterium</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ffff44;"></div>
                <span>Food Source</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff4444;"></div>
                <span>Trail</span>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        const startBtn = document.getElementById('startBtn');
        
        let bacterium;
        let foodSource;
        let trail = [];
        let isRunning = false;
        let hasReachedFood = false;
        let startTime = null;
        let endTime = null;
        
        class Bacterium {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.angle = Math.random() * 2 * Math.PI;
                this.speed = 2;
                this.state = 'run';
                this.runTime = 0;
                this.tumbleTime = 0;
                this.runDuration = 30 + Math.random() * 40;
                this.tumbleDuration = 5 + Math.random() * 10;
                this.lastConcentration = 0;
                this.size = 4;
            }
            
            update() {
                if (hasReachedFood || !isRunning) return;
                
                // Add current position to trail
                trail.push({x: this.x, y: this.y, time: Date.now()});
                
                // Check if reached food source
                const distToFood = Math.sqrt((this.x - foodSource.x) ** 2 + (this.y - foodSource.y) ** 2);
                if (distToFood < 15) {
                    hasReachedFood = true;
                    endTime = Date.now();
                    return;
                }
                
                const currentConcentration = this.getFoodConcentration();
                
                if (this.state === 'run') {
                    // Move in current direction
                    this.x += Math.cos(this.angle) * this.speed;
                    this.y += Math.sin(this.angle) * this.speed;
                    
                    this.runTime++;
                    
                    // Chemotaxis: run longer when going up gradient (increased bias)
                    let runProbability = 0.95;
                    if (currentConcentration > this.lastConcentration) {
                        runProbability = 0.999; // Much longer runs up gradient
                    } else if (currentConcentration < this.lastConcentration) {
                        runProbability = 0.85; // Much more frequent tumbles down gradient
                    }
                    
                    if (this.runTime > this.runDuration || Math.random() > runProbability) {
                        this.state = 'tumble';
                        this.runTime = 0;
                        this.tumbleDuration = 5 + Math.random() * 10;
                    }
                } else {
                    // Tumbling - random direction changes
                    this.angle += (Math.random() - 0.5) * 0.8;
                    this.tumbleTime++;
                    
                    if (this.tumbleTime > this.tumbleDuration) {
                        this.state = 'run';
                        this.tumbleTime = 0;
                        this.runDuration = 30 + Math.random() * 40;
                    }
                }
                
                this.lastConcentration = currentConcentration;
                
                // Bounce off walls
                if (this.x < 10 || this.x > canvas.width - 10 || this.y < 10 || this.y > canvas.height - 10) {
                    this.angle += Math.PI + (Math.random() - 0.5) * 0.5;
                    this.x = Math.max(10, Math.min(canvas.width - 10, this.x));
                    this.y = Math.max(10, Math.min(canvas.height - 10, this.y));
                }
            }
            
            getFoodConcentration() {
                const dist = Math.sqrt((this.x - foodSource.x) ** 2 + (this.y - foodSource.y) ** 2);
                return 100 / (1 + dist * 0.01);
            }
            
            draw() {
                // Draw bacterium
                if (hasReachedFood) {
                    ctx.fillStyle = '#00ff44'; // Green when reached food
                } else {
                    ctx.fillStyle = this.state === 'run' ? '#4444ff' : '#6666ff';
                }
                
                ctx.beginPath();
                ctx.ellipse(this.x, this.y, this.size, this.size * 1.5, this.angle, 0, 2 * Math.PI);
                ctx.fill();
                
                // Draw flagella
                if (!hasReachedFood) {
                    ctx.strokeStyle = this.state === 'tumble' ? '#8888ff' : '#6666ff';
                    ctx.lineWidth = 1;
                    for (let i = 0; i < 3; i++) {
                        const flagellaAngle = this.angle + Math.PI + (i - 1) * 0.3;
                        const flagellaLength = 8 + Math.sin(Date.now() * 0.01 + i) * 2;
                        ctx.beginPath();
                        ctx.moveTo(this.x, this.y);
                        ctx.lineTo(
                            this.x + Math.cos(flagellaAngle) * flagellaLength,
                            this.y + Math.sin(flagellaAngle) * flagellaLength
                        );
                        ctx.stroke();
                    }
                }
                
                // Direction indicator during runs
                if (this.state === 'run' && !hasReachedFood && isRunning) {
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(
                        this.x + Math.cos(this.angle) * 12,
                        this.y + Math.sin(this.angle) * 12
                    );
                    ctx.stroke();
                }
            }
        }
        
        class FoodSource {
            constructor(x, y) {
                this.x = x;
                this.y = y;
            }
            
            draw() {
                // Draw concentration gradient covering entire screen
                const maxDist = Math.sqrt(canvas.width ** 2 + canvas.height ** 2);
                const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, maxDist);
                gradient.addColorStop(0, 'rgba(68, 255, 68, 0.3)');
                gradient.addColorStop(0.3, 'rgba(68, 255, 68, 0.15)');
                gradient.addColorStop(0.6, 'rgba(68, 255, 68, 0.05)');
                gradient.addColorStop(1, 'rgba(68, 255, 68, 0)');
                
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                // Draw food source
                ctx.fillStyle = '#ffff44';
                ctx.strokeStyle = '#ffcc00';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, 12, 0, 2 * Math.PI);
                ctx.fill();
                ctx.stroke();
            }
        }
        
        function drawTrail() {
            if (trail.length < 2) return;
            
            ctx.strokeStyle = '#ff4444';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            
            // Draw trail with fading effect
            for (let i = 1; i < trail.length; i++) {
                const alpha = i / trail.length * 0.8;
                ctx.strokeStyle = `rgba(255, 68, 68, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(trail[i-1].x, trail[i-1].y);
                ctx.lineTo(trail[i].x, trail[i].y);
                ctx.stroke();
            }
        }
        
        function formatTime(milliseconds) {
            const totalSeconds = Math.floor(milliseconds / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${minutes} min${minutes !== 1 ? 's' : ''} and ${seconds} second${seconds !== 1 ? 's' : ''}`;
        }
        
        function initSimulation() {
            bacterium = new Bacterium(50, 50);
            foodSource = new FoodSource(canvas.width - 100, canvas.height - 100);
            trail = [];
            hasReachedFood = false;
            isRunning = false;
            startTime = null;
            endTime = null;
            startBtn.textContent = 'Start';
            startBtn.disabled = false;
        }
        
        function startSimulation() {
            if (!isRunning && !hasReachedFood) {
                isRunning = true;
                startTime = Date.now();
                startBtn.textContent = 'Running...';
                startBtn.disabled = true;
            }
        }
        
        function animate() {
            // Clear canvas
            ctx.fillStyle = 'rgba(0, 17, 34, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw food source
            foodSource.draw();
            
            // Draw trail
            drawTrail();
            
            // Update and draw bacterium
            bacterium.update();
            bacterium.draw();
            
            // Show completion message with time
            if (hasReachedFood && startTime && endTime) {
                const elapsedTime = endTime - startTime;
                const timeString = formatTime(elapsedTime);
                
                ctx.fillStyle = '#00ff44';
                ctx.font = '20px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(`Food Source Reached! It took your bacteria ${timeString}`, canvas.width / 2, 30);
            } else if (!isRunning && !hasReachedFood) {
                // Show start message
                ctx.fillStyle = '#ffffff';
                ctx.font = '16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('Click Start to begin the bacterial journey!', canvas.width / 2, 30);
            }
            
            requestAnimationFrame(animate);
        }
        
        function resetSimulation() {
            initSimulation();
        }
        
        // Initialize and start
        initSimulation();
        animate();
    </script>
</body>
</html>
