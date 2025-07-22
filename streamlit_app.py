import streamlit as st
import streamlit.components.v1 as components

def bacteria_animation():
    """Display the bacterial run and tumble animation in Streamlit"""
    
    # The HTML code for the animation
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bacterial Run and Tumble Motion</title>
        <style>
            body {
                margin: 0;
                padding: 10px;
                background: linear-gradient(135deg, #0f0f23, #1a1a3a);
                color: white;
                font-family: 'Arial', sans-serif;
                box-sizing: border-box;
            }
            
            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                max-width: 100vw;
            }
            
            .title {
                font-size: clamp(18px, 4vw, 24px);
                font-weight: bold;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00ff88, #00ccff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
                line-height: 1.2;
            }
            
            .description {
                font-size: clamp(12px, 3vw, 14px);
                margin-bottom: 15px;
                text-align: center;
                opacity: 0.8;
                max-width: 95%;
                line-height: 1.4;
            }
            
            #canvas {
                border: 2px solid #333;
                border-radius: 10px;
                background: radial-gradient(circle at center, #001122, #000000);
                box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
                max-width: 95vw;
                height: auto;
                display: block;
            }
            
            .controls {
                margin-top: 15px;
                display: flex;
                gap: 15px;
                align-items: center;
                justify-content: center;
                width: 100%;
            }
            
            button {
                padding: 10px 20px;
                background: linear-gradient(45deg, #00ff88, #00ccff);
                border: none;
                border-radius: 8px;
                color: #000;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
                font-size: clamp(14px, 3.5vw, 16px);
                min-height: 44px; /* iOS touch target minimum */
                touch-action: manipulation;
            }
            
            button:hover, button:active {
                transform: scale(1.05);
            }
            
            .legend {
                margin-top: 15px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
                gap: 15px;
                font-size: clamp(11px, 2.5vw, 12px);
                width: 95%;
                max-width: 400px;
                justify-items: center;
            }
            
            .legend-item {
                display: flex;
                align-items: center;
                gap: 8px;
                justify-content: center;
            }
            
            .legend-color {
                width: 14px;
                height: 14px;
                border-radius: 50%;
                flex-shrink: 0;
            }
            
            /* Mobile-specific optimizations */
            @media (max-width: 768px) {
                body {
                    padding: 5px;
                }
                
                .title {
                    margin-bottom: 8px;
                }
                
                .description {
                    margin-bottom: 12px;
                }
                
                .controls {
                    margin-top: 12px;
                    gap: 12px;
                }
                
                .legend {
                    margin-top: 12px;
                    gap: 10px;
                }
            }
            
            /* Prevent zoom on double-tap */
            * {
                touch-action: manipulation;
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
            
            <canvas id="canvas"></canvas>
            
            <div class="controls">
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
            
            // Make canvas responsive
            function resizeCanvas() {
                const container = canvas.parentElement;
                const containerWidth = container.clientWidth;
                const maxWidth = Math.min(containerWidth * 0.95, 800);
                const aspectRatio = 500 / 800;
                
                canvas.width = maxWidth;
                canvas.height = maxWidth * aspectRatio;
                canvas.style.width = maxWidth + 'px';
                canvas.style.height = (maxWidth * aspectRatio) + 'px';
                
                // Reinitialize positions based on new canvas size
                if (bacterium && foodSource) {
                    bacterium.x = Math.min(bacterium.x, canvas.width - 10);
                    bacterium.y = Math.min(bacterium.y, canvas.height - 10);
                    foodSource.x = canvas.width - 50;
                    foodSource.y = canvas.height - 50;
                }
            }
            
            // Call on load and resize
            window.addEventListener('resize', resizeCanvas);
            window.addEventListener('load', resizeCanvas);
            
            let bacterium;
            let foodSource;
            let trail = [];
            let isRunning = true;
            let hasReachedFood = false;
            
            class Bacterium {
                constructor(x, y) {
                    this.x = x;
                    this.y = y;
                    this.angle = Math.random() * 2 * Math.PI;
                    this.speed = Math.max(1.5, canvas.width * 0.0025); // Scale speed with canvas size
                    this.state = 'run';
                    this.runTime = 0;
                    this.tumbleTime = 0;
                    this.runDuration = 30 + Math.random() * 40;
                    this.tumbleDuration = 5 + Math.random() * 10;
                    this.lastConcentration = 0;
                    this.size = Math.max(3, canvas.width * 0.005); // Scale size with canvas
                }
                
                update() {
                    if (hasReachedFood) return;
                    
                    trail.push({x: this.x, y: this.y, time: Date.now()});
                    
                    const distToFood = Math.sqrt((this.x - foodSource.x) ** 2 + (this.y - foodSource.y) ** 2);
                    if (distToFood < 15) {
                        hasReachedFood = true;
                        return;
                    }
                    
                    const currentConcentration = this.getFoodConcentration();
                    
                    if (this.state === 'run') {
                        this.x += Math.cos(this.angle) * this.speed;
                        this.y += Math.sin(this.angle) * this.speed;
                        
                        this.runTime++;
                        
                        let runProbability = 0.95;
                        if (currentConcentration > this.lastConcentration) {
                            runProbability = 0.999;
                        } else if (currentConcentration < this.lastConcentration) {
                            runProbability = 0.85;
                        }
                        
                        if (this.runTime > this.runDuration || Math.random() > runProbability) {
                            this.state = 'tumble';
                            this.runTime = 0;
                            this.tumbleDuration = 5 + Math.random() * 10;
                        }
                    } else {
                        this.angle += (Math.random() - 0.5) * 0.8;
                        this.tumbleTime++;
                        
                        if (this.tumbleTime > this.tumbleDuration) {
                            this.state = 'run';
                            this.tumbleTime = 0;
                            this.runDuration = 30 + Math.random() * 40;
                        }
                    }
                    
                    this.lastConcentration = currentConcentration;
                    
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
                    if (hasReachedFood) {
                        ctx.fillStyle = '#00ff44';
                    } else {
                        ctx.fillStyle = this.state === 'run' ? '#4444ff' : '#6666ff';
                    }
                    
                    ctx.beginPath();
                    ctx.ellipse(this.x, this.y, this.size, this.size * 1.5, this.angle, 0, 2 * Math.PI);
                    ctx.fill();
                    
                    if (!hasReachedFood) {
                        ctx.strokeStyle = this.state === 'tumble' ? '#8888ff' : '#6666ff';
                        ctx.lineWidth = Math.max(1, canvas.width * 0.001);
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
                    
                    if (this.state === 'run' && !hasReachedFood) {
                        ctx.strokeStyle = '#ffffff';
                        ctx.lineWidth = Math.max(1.5, canvas.width * 0.002);
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
                    const maxDist = Math.sqrt(canvas.width ** 2 + canvas.height ** 2);
                    const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, maxDist);
                    gradient.addColorStop(0, 'rgba(68, 255, 68, 0.3)');
                    gradient.addColorStop(0.3, 'rgba(68, 255, 68, 0.15)');
                    gradient.addColorStop(0.6, 'rgba(68, 255, 68, 0.05)');
                    gradient.addColorStop(1, 'rgba(68, 255, 68, 0)');
                    
                    ctx.fillStyle = gradient;
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    const foodSize = Math.max(8, canvas.width * 0.015);
                    ctx.fillStyle = '#ffff44';
                    ctx.strokeStyle = '#ffcc00';
                    ctx.lineWidth = Math.max(1.5, canvas.width * 0.002);
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, foodSize, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.stroke();
                }
            }
            
            function drawTrail() {
                if (trail.length < 2) return;
                
                ctx.strokeStyle = '#ff4444';
                ctx.lineWidth = Math.max(1.5, canvas.width * 0.002);
                ctx.lineCap = 'round';
                
                for (let i = 1; i < trail.length; i++) {
                    const alpha = i / trail.length * 0.8;
                    ctx.strokeStyle = `rgba(255, 68, 68, ${alpha})`;
                    ctx.beginPath();
                    ctx.moveTo(trail[i-1].x, trail[i-1].y);
                    ctx.lineTo(trail[i].x, trail[i].y);
                    ctx.stroke();
                }
            }
            
            function initSimulation() {
                resizeCanvas(); // Ensure canvas is properly sized
                bacterium = new Bacterium(30, 30);
                foodSource = new FoodSource(canvas.width - 50, canvas.height - 50);
                trail = [];
                hasReachedFood = false;
            }
            
            function animate() {
                ctx.fillStyle = 'rgba(0, 17, 34, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                foodSource.draw();
                drawTrail();
                bacterium.update();
                bacterium.draw();
                
                if (hasReachedFood) {
                    ctx.fillStyle = '#00ff44';
                    ctx.font = `${Math.max(16, canvas.width * 0.025)}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.fillText('Food Source Reached!', canvas.width / 2, 30);
                }
                
                requestAnimationFrame(animate);
            }
            
            function resetSimulation() {
                initSimulation();
            }
            
            // Initialize after a short delay to ensure DOM is ready
            setTimeout(() => {
                initSimulation();
                animate();
            }, 100);
        </script>
    </body>
    </html>
    """
    
    # Display the HTML component in Streamlit
    components.html(html_code, height=700)

# Example usage in your Streamlit app
def main():
    st.set_page_config(page_title="Bacterial Motion", layout="wide")
    
    st.title("🦠 Bacterial Chemotaxis Simulation")
    
    st.markdown("""
    This simulation demonstrates how bacteria use **run and tumble motion** to navigate toward food sources.
    The bacterium alternates between straight runs and random tumbles, with longer runs when moving up
    the chemical concentration gradient.
    """)
    
    # Display the animation
    bacteria_animation()
    
    st.markdown("""
    ### How it works:
    - **Blue bacterium**: Changes between running (with direction arrow) and tumbling states
    - **Red trail**: Shows the path taken by the bacterium
    - **Green gradient**: Chemical concentration field from the food source
    - **Yellow circle**: Food source target
    
    The bacterium uses chemotaxis - it runs longer when detecting increasing concentrations
    and tumbles more frequently when concentrations decrease, gradually biasing its movement toward food.
    """)

if __name__ == "__main__":
    main()
