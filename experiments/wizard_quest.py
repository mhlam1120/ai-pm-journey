import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="Retro Platformer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Streamlit UI Layer
st.title("🕹️ Scrolling Platformer Adventure")
st.markdown("""
<style>
    /* Make the iframe container centered */
    .stMainBlockContainer {
        display: flex;
        justify_content: center;
    }
    /* Hide the sidebar expander to keep focus on game */
    [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# 3. The Game Code (Consolidated HTML/JS)
game_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scrolling Platformer Adventure</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        /* Custom CSS for a retro, pixelated look */
        :root {
            /* Base Colors (These will be dynamically overridden by JavaScript themes) */
            --primary-color: #48bb78; 
            --player-head-color: #48bb78; 
            --player-body-color: #9f7aea; 
            --enemy-color: #6b46c1; 
            --projectile-color: #ecc94b; 
            --sky-top: #63b3ed; 
            --sky-bottom: #90cdf4; 
            --platform-color: #2d3748; 
            --font: 'Press Start 2P', cursive;
        }

        body {
            font-family: var(--font);
            background-color: #0e1117; /* Matches Streamlit Dark Mode default */
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 0px; 
            overflow: hidden; /* Prevent body scrollbars */
        }

        #game-container {
            border: 8px solid var(--platform-color);
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(72, 187, 120, 0.7);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 800px;
            position: relative; 
            transition: border-color 0.5s;
        }

        #game-canvas {
            background-color: var(--sky-bottom);
            display: block;
            width: 100%;
            height: 450px; 
        }

        .info-bar {
            background-color: var(--platform-color);
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: white;
            transition: background-color 0.5s;
        }

        .control-button {
            background-color: var(--primary-color);
            color: black;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            border-radius: 0.25rem;
            font-size: 0.6rem;
            cursor: pointer;
            transition: transform 0.1s;
            border: 2px solid #fff;
            box-shadow: 3px 3px 0 #000;
            user-select: none;
            line-height: 1;
        }

        .control-button:active {
            transform: translateY(2px);
            box-shadow: 1px 1px 0 #000;
        }

        .controls-info {
            background-color: var(--platform-color);
            padding: 0.75rem 1rem;
            font-size: 0.5rem;
            text-align: center;
            border-top: 2px dashed var(--primary-color);
            transition: background-color 0.5s;
        }

        /* Modal styling */
        #message-box {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.95);
            color: white;
            padding: 1.5rem;
            border: 4px solid var(--player-head-color);
            border-radius: 8px;
            text-align: center;
            z-index: 10;
            box-shadow: 0 0 40px rgba(72, 187, 120, 0.8);
            width: 90%;
            max-width: 500px;
            line-height: 1.5;
            font-size: 0.8rem;
            max-height: 95%; /* Ensure it fits in iframe */
            overflow-y: auto; /* Scroll if content is too tall */
        }

        #message-box button {
            margin-top: 1rem;
            background-color: var(--player-head-color);
            color: white;
            font-size: 0.8rem;
        }
        
        #flash-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0;
            z-index: 5;
            transition: opacity 0.1s;
        }

        .buy-button.bought {
            background-color: #4b5563 !important; 
            color: #d1d5db !important; 
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }
    </style>
</head>
<body>

<div id="game-container">
    <div id="flash-overlay"></div>
    
    <div class="info-bar">
        <span id="score-display">LEVEL 1 | SCORE: 000</span>
        <span id="lives-display">LIVES: 3</span>
        <span id="objects-display">OBJECTS: 0/5</span>
    </div>

    <canvas id="game-canvas"></canvas>

    <div class="controls-info">
        CONTROLS: ARROW KEYS (Move/Jump) | SPACE (Shoot)
        <div class="flex justify-center mt-2" id="mobile-controls">
            </div>
    </div>
</div>

<div id="message-box" style="display: block;">
    <p>SCROLLING PLATFORMER ADVENTURE</p>
    <p class="text-xs mt-3">Collect 5 objects, then defeat the Mini Boss to win! (Collectibles grant a 20% boost)</p>
    <button class="control-button" id="start-button">START GAME</button>
</div>

<script type="module">
    // --- CANVAS AND INITIAL SETUP ---
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');
    const scoreDisplay = document.getElementById('score-display');
    const livesDisplay = document.getElementById('lives-display');
    const objectsDisplay = document.getElementById('objects-display');
    const messageBox = document.getElementById('message-box');
    const startButton = document.getElementById('start-button');
    const flashOverlay = document.getElementById('flash-overlay');
    const gameContainer = document.getElementById('game-container');

    const GAME_WIDTH = 800;
    const GAME_HEIGHT = 450;
    canvas.width = GAME_WIDTH;
    canvas.height = GAME_HEIGHT;

    // --- GAME CONSTANTS: UPDATED FOR FASTER SPEED ---
    const GRAVITY = 0.6; // Doubled gravity for snappier jumps
    const PLAYER_SPEED_BASE = 5.5; // Much faster movement
    const PROJECTILE_SPEED_BASE = 9.0; // Faster shooting
    const PROJECTILE_DAMAGE_BASE = 1; 
    const ENEMY_SPEED_BASE = 1.2; // Faster enemies
    const BOSS_HP_BASE = 5; 
    const JUMP_POWER = -13; // Higher jump to compensate for gravity
    
    const SHOOT_COOLDOWN = 250; // Reduced cooldown slightly
    const GROUND_Y = GAME_HEIGHT - 30; 
    const VIEWPORT_THRESHOLD = GAME_WIDTH * 0.4; 
    const LEVEL_END_X = 2500; 
    const OBJECT_COUNT = 5;
    const BOOST_PERCENTAGE = 0.20; 
    const BOSS_TRIGGER_X = 1800; 
    
    const ARROW_INTERVAL_L2 = 1500; 
    const ARROW_INTERVAL_L3 = 800; 
    const LASER_CHARGE_TIME = 4000; 
    const LASER_DELAY = 1500; 
    const LASER_DURATION = 1200; 
    const LASER_W = 600; 
    const LASER_H = 15; 

    let PLAYER_SPEED = PLAYER_SPEED_BASE; 
    let PROJECTILE_SPEED = PROJECTILE_SPEED_BASE; 
    let ENEMY_SPEED = ENEMY_SPEED_BASE; 
    let BOSS_HP = BOSS_HP_BASE; 

    let playerMaxLives = 3; 
    let playerSpeedMultiplier = 1;
    let playerAttackMultiplier = 1;
    let isInvisible = false; 
    
    const PRICE_HEALTH = 1500;
    const PRICE_SPEED = 2500;
    const PRICE_ATTACK = 1000;
    
    const PURCHASED_UPGRADES = { health: false, speed: false, attack: false };

    let currentLevel = 1;
    let persistentScore = 0;
    const collectibleWorldXs = [400, 650, 900, 1300, 1900];

    let gameActive = false;
    let player;
    let enemies = [];
    let projectiles = [];
    let collectibles = [];
    let boss = null;
    let keys = {};
    let lastShotTime = 0;
    let worldOffset = 0; 
    let collectedObjects = 0;
    let boostActive = false;
    let isBossActive = false;
    let screenFlashTimer = 0; 
    let levelPlatforms = []; 

    const colors = {
        playerHead: '#48bb78',
        playerBody: '#9f7aea',
        enemy: '#6b46c1', 
        projectile: '#ecc94b', 
        skyTop: '#63b3ed', 
        skyBottom: '#90cdf4', 
        platform: '#2d3748', 
    };

    function generateLevel(level) {
        PLAYER_SPEED = PLAYER_SPEED_BASE * playerSpeedMultiplier;
        PROJECTILE_SPEED = PROJECTILE_SPEED_BASE * playerSpeedMultiplier;
        
        let levelIndex = (level - 1) % 3; 
        
        if (level === 4) {
            ENEMY_SPEED = 0; 
            BOSS_HP = 50; 
            
            const theme = { skyTop: '#1a202c', skyBottom: '#4c51bf', platform: '#000000', primary: '#fbd38d' }; 
            
            const finalPlatforms = [
                [0, GROUND_Y, LEVEL_END_X * 2, 30], 
                [500, GROUND_Y - 100, 200, 10], 
                [1200, GROUND_Y - 150, 150, 10],
            ];

            isBossActive = true;
            boss = new Boss(2000, GROUND_Y - 60); 
            boss.initialHP = BOSS_HP;
            boss.hp = BOSS_HP;
            boss.vx = ENEMY_SPEED_BASE * 1.5; 
            
            const colorTheme = theme;
            
            return { 
                platforms: finalPlatforms, 
                enemies: [], 
                collectibles: []
            };
        }

        ENEMY_SPEED = ENEMY_SPEED_BASE * (1 + levelIndex * 0.5); 
        BOSS_HP = Math.ceil(BOSS_HP_BASE * (1 + levelIndex * 0.5)); 
        console.log(`Starting Level ${level}. Enemy Speed: ${ENEMY_SPEED.toFixed(1)}, Boss HP: ${BOSS_HP}`);

        const themes = [
            { skyTop: '#63b3ed', skyBottom: '#90cdf4', platform: '#2d3748', primary: '#48bb78' },
            { skyTop: '#f6ad55', skyBottom: '#fbd38d', platform: '#9b2c2c', primary: '#f6ad55' },
            { skyTop: '#4c51bf', skyBottom: '#9f7aea', platform: '#1a202c', primary: '#9f7aea' },
        ];
        const colorTheme = themes[levelIndex];

        const shift = levelIndex * 50; 
        const newPlatforms = [
            [0, GROUND_Y, LEVEL_END_X, 30], 
            [300 + shift, GROUND_Y - 50, 100, 10],
            [450 + shift, GROUND_Y - 100, 120, 10],
            [700 + shift, GROUND_Y - 50, 100, 10],
            [1000 + shift, GROUND_Y - 150, 200, 10],
            [1400 + shift, GROUND_Y - 50, 80, 10],
            [1600 + shift, GROUND_Y - 100, 150, 10],
            [2100 + shift, GROUND_Y - 50, 100, 10], 
        ];
        
        let newEnemies = [];
        const enemyCount = 3 + (levelIndex + 1) * 2; 
        for (let i = 0; i < enemyCount; i++) {
            const xOffset = 200 + (i * (BOSS_TRIGGER_X * 0.8) / enemyCount) + (levelIndex * 20) + (Math.random() * 50);
            const yOffset = (i % 3 === 0) ? 0 : (i % 3 === 1 ? 50 : 100);
            newEnemies.push({ worldX: xOffset, worldY: GROUND_Y - 25 - yOffset });
        }

        const collectibleY = GROUND_Y - 50 - (levelIndex * 15);
        const newCollectibles = collectibleWorldXs.map(x => new Collectible(x, collectibleY));

        return { 
            platforms: newPlatforms, 
            enemies: newEnemies.map(data => new Enemy(data.worldX, data.worldY)), 
            collectibles: newCollectibles 
        };
    }

    function applyBoost() {
        if (!boostActive && collectedObjects >= OBJECT_COUNT) {
            PLAYER_SPEED = PLAYER_SPEED_BASE * playerSpeedMultiplier * (1 + BOOST_PERCENTAGE);
            PROJECTILE_SPEED = PROJECTILE_SPEED_BASE * playerSpeedMultiplier * (1 + BOOST_PERCENTAGE);
            boostActive = true;
            console.log(`Boost applied! Speed: ${PLAYER_SPEED.toFixed(1)}, Projectile Speed: ${PROJECTILE_SPEED.toFixed(1)}`);
        }
    }

    class Player {
        constructor() {
            this.w = 20;
            this.h = 30;
            this.x = 50; 
            this.worldX = 50; 
            this.y = GROUND_Y - this.h;
            this.vx = 0;
            this.vy = 0;
            this.isGrounded = true;
            this.score = 0; 
            this.lives = playerMaxLives; 
            this.invincible = false;
            this.invincibleTimer = 0;
            this.facingDirection = 1; 
        }

        draw() {
            const isFlashing = this.invincible && Math.floor(this.invincibleTimer / 10) % 2 === 0;
            const isSolid = !isFlashing && !(isInvisible && Math.floor(performance.now() / 100) % 2 === 0);

            if (!isSolid) {
                return;
            }

            const screenX = this.x;
            const screenY = this.y;
            const w = this.w;
            const h = this.h;
            const dir = this.facingDirection;

            ctx.fillStyle = colors.playerBody; 
            ctx.fillRect(screenX, screenY + h * 0.4, w, h * 0.6); 

            ctx.fillStyle = colors.playerHead; 
            ctx.fillRect(screenX + 2, screenY, w - 4, h * 0.45);

            ctx.fillStyle = '#1A202C'; 
            ctx.beginPath();
            ctx.moveTo(screenX + w * 0.5, screenY - 10); 
            ctx.lineTo(screenX, screenY + 5); 
            ctx.lineTo(screenX + w, screenY + 5); 
            ctx.closePath();
            ctx.fill();

            const staffX = screenX + w * 0.5 + dir * (w * 0.7);
            const staffY = screenY + h * 0.2;
            ctx.fillStyle = '#9B2C2C'; 
            ctx.fillRect(staffX, staffY, 3, h * 0.8);
            
            ctx.fillStyle = '#FBD38D'; 
            ctx.fillRect(staffX - 2, staffY - 5, 7, 7); 
        }

        update() {
            this.vy += GRAVITY;
            this.y += this.vy;

            this.vx = 0;
            if (keys['ArrowLeft']) {
                this.vx = -PLAYER_SPEED;
                this.facingDirection = -1;
            }
            if (keys['ArrowRight']) {
                this.vx = PLAYER_SPEED;
                this.facingDirection = 1;
            }
            
            this.worldX += this.vx;

            if (this.vx > 0 && this.x > GAME_WIDTH - VIEWPORT_THRESHOLD) {
                worldOffset += this.vx;
                this.x = GAME_WIDTH - VIEWPORT_THRESHOLD;
            } else if (this.vx < 0 && this.x < VIEWPORT_THRESHOLD) {
                if (worldOffset > 0) {
                    worldOffset += this.vx;
                    this.x = VIEWPORT_THRESHOLD;
                } else {
                    this.x += this.vx;
                }
            } else {
                this.x += this.vx;
            }
            
            if (worldOffset < 0) worldOffset = 0;
            if (worldOffset === 0 && this.x < 0) this.x = 0;
            if (this.x + this.w > GAME_WIDTH) this.x = GAME_WIDTH - this.w;


            this.isGrounded = false;
            let onPlatform = false;

            for (const p of levelPlatforms) {
                const pScreenX = p[0] - worldOffset;
                const pY = p[1];
                const pW = p[2];
                
                if (this.x < pScreenX + pW &&
                    this.x + this.w > pScreenX &&
                    this.y + this.h <= pY + this.vy && 
                    this.y + this.h + this.vy >= pY) { 
                    
                    this.y = pY - this.h;
                    this.vy = 0;
                    onPlatform = true;
                    break;
                }
            }
            this.isGrounded = onPlatform;
            
            if (this.y + this.h > GROUND_Y) {
                this.y = GROUND_Y - this.h;
                this.vy = 0;
                this.isGrounded = true;
            }

            if (this.invincible) {
                this.invincibleTimer--;
                if (this.invincibleTimer <= 0) {
                    this.invincible = false;
                }
            }
        }
        
        jump() {
            if (this.isGrounded) {
                this.vy = JUMP_POWER;
                this.isGrounded = false;
            }
        }

        takeDamage() {
            if (!this.invincible && !isInvisible) {
                this.lives--;
                this.invincible = true;
                this.invincibleTimer = 120; 
                if (this.lives <= 0) {
                    gameOver();
                } else {
                    updateUI();
                }
            }
        }

        reset() {
            this.x = 50;
            this.worldX = 50;
            this.y = GROUND_Y - this.h;
            this.vx = 0;
            this.vy = 0;
            this.isGrounded = true;
            this.lives = playerMaxLives; 
            this.score = 0;
            this.invincible = false;
            this.invincibleTimer = 0;
            this.facingDirection = 1;
        }
    }

    class Enemy {
        constructor(worldX, worldY) {
            this.w = 25;
            this.h = 25;
            this.worldX = worldX;
            this.worldY = worldY;
            this.vx = Math.random() > 0.5 ? ENEMY_SPEED : -ENEMY_SPEED; 
            this.vy = 0; 
            this.isGrounded = false; 
            this.isAlive = true;
            this.scoreValue = 100;
        }
        
        draw() {
            if (!this.isAlive) return;
            const screenX = this.worldX - worldOffset;
            const screenY = this.worldY;
            const w = this.w;
            const h = this.h;
            
            ctx.fillStyle = colors.enemy;
            ctx.beginPath();
            ctx.ellipse(screenX + w / 2, screenY + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = 'white';
            const eyeX = screenX + w / 2 + (this.vx > 0 ? 5 : -5);
            ctx.beginPath();
            ctx.arc(eyeX, screenY + h / 3, 4, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(eyeX, screenY + h / 3, 2, 0, Math.PI * 2);
            ctx.fill();
        }

        update() {
            if (!this.isAlive) return;

            this.vy += GRAVITY;
            this.worldY += this.vy;
            this.worldX += this.vx;
            this.isGrounded = false;
            
            for (const p of levelPlatforms) {
                const pWorldX = p[0];
                const pY = p[1];
                const pW = p[2];
                
                if (this.worldX + this.w > pWorldX && this.worldX < pWorldX + pW) {
                    if (this.worldY + this.h >= pY && this.worldY + this.h <= pY + GRAVITY) {
                        this.worldY = pY - this.h; 
                        this.vy = 0;
                        this.isGrounded = true;
                        
                        const nextWorldX = this.worldX + this.vx;
                        const edgePadding = 2; 
                        
                        if (this.vx > 0 && nextWorldX + this.w > pWorldX + pW + edgePadding) {
                            this.vx *= -1; 
                        } 
                        else if (this.vx < 0 && nextWorldX < pWorldX - edgePadding) {
                            this.vx *= -1; 
                        }
                        
                        break; 
                    }
                }
            }
            
            if (this.worldX < 0) {
                this.worldX = 0;
                this.vx *= -1;
            }
        }

        getScreenPosition() {
            return {
                x: this.worldX - worldOffset,
                y: this.worldY,
                w: this.w,
                h: this.h
            };
        }
    }

    class Boss extends Enemy {
        constructor(worldX, worldY) {
            super(worldX, worldY);
            this.w = 60; 
            this.h = 60; 
            this.initialHP = BOSS_HP; 
            this.hp = this.initialHP;
            this.vx = ENEMY_SPEED * 0.5; 
            this.scoreValue = 500 * currentLevel; 

            this.lastArrowTime = performance.now();
            this.lastUpdateTime = performance.now(); 
            this.attackState = 'ARROW_ATTACK'; 
            this.laserTimer = 0; 
            this.laserDirection = 1; 
        }

        shootArrow() {
            const screenX = this.worldX - worldOffset;
            
            this.laserDirection = (player.worldX - this.worldX) > 0 ? 1 : -1;

            const startX = screenX + (this.laserDirection === 1 ? this.w * 0.8 : -20); 
            const startY = this.worldY + this.h * 0.5;
            
            projectiles.push(new Projectile(startX, startY, this.laserDirection, 'arrow'));
        }

        draw() {
            if (!this.isAlive) return;
            ctx.shadowBlur = 0; 

            const screenX = this.worldX - worldOffset;
            const screenY = this.worldY;
            const w = this.w;
            const h = this.h;
            
            if (currentLevel < 4) {
                const centerX = screenX + w / 2;
                const centerY = screenY + h / 2;
                const radius = w / 2 - 5; 
                
                ctx.shadowColor = 'rgba(0,0,0,0.5)';
                ctx.shadowBlur = 4;
                ctx.shadowOffsetY = 4;
                
                ctx.fillStyle = '#4A5568'; 
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = '#B7942E'; 
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius * 0.8, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = '#718096';
                ctx.fillRect(centerX - 10, centerY - 15, 5, 5);
                ctx.fillRect(centerX + 5, centerY + 10, 5, 5);
                ctx.fillRect(centerX - 5, centerY, 10, 5);

                ctx.shadowBlur = 0;
                ctx.shadowOffsetY = 0;
                ctx.fillStyle = '#C53030'; 
                ctx.fillRect(centerX - 1, screenY - 5, 3, 10); 
                ctx.beginPath();
                ctx.arc(centerX, screenY - 5, 4, 0, Math.PI * 2); 
                ctx.fill();
                
                const legColor = '#718096'; 
                const jointColor = '#1A202C'; 
                const numLegs = 4;
                const legLength = w * 0.8;
                const segments = 2; 

                for (let i = 0; i < numLegs * 2; i++) {
                    const isLeft = i % 2 === 0;
                    const dir = isLeft ? -1 : 1; 
                    let currentX = centerX + dir * radius;
                    let currentY = centerY;
                    
                    for (let s = 0; s < segments; s++) {
                        ctx.strokeStyle = legColor;
                        ctx.lineWidth = 2;
                        ctx.lineCap = 'round';
                        
                        const angleMultiplier = isLeft ? (i / 2) : ((i-1) / 2);
                        let nextX, nextY;
                        
                        if (s === 0) { 
                            nextX = currentX + dir * legLength * 0.3;
                            nextY = currentY + angleMultiplier * 2; 
                        } else { 
                            nextX = currentX + dir * legLength * 0.2;
                            nextY = currentY + legLength * 0.3;
                        }

                        ctx.beginPath();
                        ctx.moveTo(currentX, currentY);
                        ctx.lineTo(nextX, nextY);
                        ctx.stroke();

                        ctx.fillStyle = jointColor;
                        ctx.beginPath();
                        ctx.arc(currentX, currentY, 2, 0, Math.PI * 2);
                        ctx.fill();

                        currentX = nextX;
                        currentY = nextY;
                    }

                    ctx.fillStyle = legColor;
                    ctx.fillRect(currentX - 1, currentY, 3, 5); 
                }
                
                ctx.shadowBlur = 0; 
                ctx.shadowColor = 'transparent';
                
            } else {
                
                ctx.shadowColor = 'red';
                ctx.shadowBlur = 15;
                
                ctx.fillStyle = '#9B2C2C'; 
                ctx.fillRect(screenX, screenY + h * 0.3, w, h * 0.7);
                
                ctx.fillStyle = 'black';
                ctx.beginPath();
                ctx.moveTo(screenX, screenY + h * 0.3);
                ctx.lineTo(screenX + w, screenY + h * 0.3);
                ctx.lineTo(screenX + w * 0.8, screenY);
                ctx.lineTo(screenX + w * 0.2, screenY);
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = '#FEEBC8'; 
                ctx.fillRect(screenX + w * 0.45, screenY + h * 0.1, w * 0.1, 5);

                ctx.shadowBlur = 0; 
                ctx.shadowColor = 'transparent';
            }

            if (currentLevel === 3) {
                const centerX = screenX + w / 2;
                const centerY = screenY + h * 0.5;
                
                if (this.attackState === 'LASER_CHARGE') {
                    const pulseRadius = 5 + Math.sin(performance.now() * 0.01) * 3;
                    ctx.fillStyle = '#FF0000';
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
                    ctx.fill();
                }
                
                if (this.attackState === 'LASER_ACTIVE') {
                    
                    const dir = this.laserDirection;
                    const startX = centerX + dir * (w / 2);
                    const endX = startX + dir * LASER_W;
                    const laserY = centerY - LASER_H / 2;
                    
                    ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
                    ctx.fillRect(startX, laserY, dir * LASER_W, LASER_H);
                    
                    ctx.shadowColor = 'red';
                    ctx.shadowBlur = 20;
                    ctx.fillStyle = 'rgba(255, 192, 203, 0.3)'; 
                    ctx.fillRect(startX, laserY - 5, dir * LASER_W, LASER_H + 10);
                    ctx.shadowBlur = 0;
                }
            }


            const hpBarWidth = (this.hp / this.initialHP) * w;
            ctx.fillStyle = 'lime';
            ctx.fillRect(screenX, screenY - 10, hpBarWidth, 5);
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 1;
            ctx.strokeRect(screenX, screenY - 10, w, 5);

            ctx.shadowBlur = 0;
            ctx.shadowColor = 'transparent';
        }
        
        takeDamage(damage) {
            this.hp -= damage; 
            if (this.hp <= 0) {
                this.isAlive = false;
                player.score += this.scoreValue;
                
                if (currentLevel === 4) { 
                     showShopScreen();
                } else {
                     levelComplete(); 
                }
            }
        }
        
        update() {
             this.vy += GRAVITY;
             this.worldY += this.vy;
             this.worldX += this.vx;
            
            const ground = levelPlatforms[0];
            const pY = ground[1];
            
            if (this.worldY + this.h >= pY) {
                this.worldY = pY - this.h; 
                this.vy = 0;
            }
            
            if (this.worldX < ground[0] || this.worldX + this.w > ground[0] + ground[2]) {
                this.vx *= -1;
                this.worldX += this.vx; 
            }

            const now = performance.now();
            const dt = now - this.lastUpdateTime;
            this.lastUpdateTime = now;

            if (currentLevel === 2 || currentLevel === 3) {
                const arrowInterval = currentLevel === 2 ? ARROW_INTERVAL_L2 : ARROW_INTERVAL_L3;

                if (this.attackState === 'ARROW_ATTACK') {
                    this.laserTimer += dt;
                    if (now - this.lastArrowTime > arrowInterval) {
                        this.shootArrow();
                        this.lastArrowTime = now;
                    }

                    if (currentLevel === 3 && this.laserTimer >= LASER_CHARGE_TIME) {
                        this.attackState = 'LASER_CHARGE';
                        this.laserTimer = 0; 
                    }
                } 
                
                else if (this.attackState === 'LASER_CHARGE') {
                    this.laserTimer += dt;
                    if (this.laserTimer >= LASER_DELAY) {
                        this.attackState = 'LASER_ACTIVE';
                        this.laserTimer = 0; 
                    }
                } 
                
                else if (this.attackState === 'LASER_ACTIVE') {
                    this.laserTimer += dt;
                    
                    if (this.laserTimer >= LASER_DURATION) {
                        this.attackState = 'ARROW_ATTACK';
                        this.laserTimer = 0; 
                        this.lastArrowTime = now; 
                    }
                }
            }
        }
    }

    class Projectile {
        constructor(x, y, direction, type = 'fireball') {
            this.type = type; 
            this.w = (type === 'arrow') ? 30 : 24; 
            this.h = (type === 'arrow') ? 5 : 12; 
            
            this.x = x; 
            this.y = y;
            this.vx = direction * PROJECTILE_SPEED; 
            this.isAlive = true;
            this.damage = (type === 'arrow') ? 1 : PROJECTILE_DAMAGE_BASE * playerAttackMultiplier; 
        }

        draw() {
            if (!this.isAlive) return;
            
            const screenX = this.x;
            const screenY = this.y;

            if (this.type === 'arrow') { 
                ctx.fillStyle = '#9B5500'; 
                ctx.fillRect(screenX, screenY + 2, this.w, 1);
                
                ctx.fillStyle = '#6b46c1'; 
                ctx.beginPath();
                if (this.vx > 0) { 
                    ctx.moveTo(screenX + this.w, screenY);
                    ctx.lineTo(screenX + this.w, screenY + this.h);
                    ctx.lineTo(screenX + this.w + 10, screenY + this.h / 2);
                } else { 
                    ctx.moveTo(screenX, screenY);
                    ctx.lineTo(screenX, screenY + this.h);
                    ctx.lineTo(screenX - 10, screenY + this.h / 2);
                }
                ctx.closePath();
                ctx.fill();

                ctx.fillStyle = '#D1D5DB'; 
                const fletchingX = this.vx > 0 ? screenX - 5 : screenX + this.w + 5;
                ctx.fillRect(fletchingX - 2, screenY, 5, this.h); 
            } else { 
                
                const flameOffset = Math.sin(performance.now() * 0.02) * 2; 
                
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#FF8C00'; 
                
                ctx.fillStyle = '#C53030'; 
                ctx.fillRect(screenX + 3 + flameOffset, screenY + 5 + flameOffset, this.w - 6, this.h - 10);
                
                ctx.fillStyle = '#DD6B20'; 
                ctx.fillRect(screenX + 5, screenY + 3 + flameOffset * 0.5, this.w - 10, this.h - 6);
                
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#FFFF66'; 
                ctx.fillStyle = '#FBD38D'; 
                ctx.fillRect(screenX + 8 - flameOffset, screenY + 6, this.w - 16, this.h - 12);

                const trailW = 5;
                const trailH = 3;
                ctx.shadowBlur = 0;
                ctx.fillStyle = 'rgba(255, 100, 0, 0.5)';
                const trailX = (this.vx > 0) ? screenX - trailW : screenX + this.w;
                ctx.fillRect(trailX, screenY - trailH / 2, trailW, trailH);

                ctx.shadowBlur = 0;
                ctx.shadowColor = 'transparent';
            }
        }

        update() {
            if (!this.isAlive) return;
            this.x += this.vx;

            if (this.x < -this.w || this.x > GAME_WIDTH) {
                this.isAlive = false;
            }
        }
    }
    
    class Collectible {
        constructor(worldX, worldY) {
            this.w = 15;
            this.h = 15;
            this.worldX = worldX;
            this.worldY = worldY;
            this.isCollected = false;
            this.frame = 0;
        }

        draw() {
            if (this.isCollected) return;
            const screenX = this.worldX - worldOffset;

            this.frame++;
            const offset = Math.sin(this.frame * 0.1) * 2;
            
            ctx.fillStyle = '#FEEBC8'; 
            ctx.beginPath();
            ctx.moveTo(screenX + this.w / 2, this.worldY + offset);
            ctx.lineTo(screenX + this.w, this.worldY + this.h / 2 + offset);
            ctx.lineTo(screenX + this.w / 2, this.worldY + this.h + offset);
            ctx.lineTo(screenX, this.worldY + this.h / 2 + offset);
            ctx.closePath();
            ctx.fill();
        }

        getScreenPosition() {
            return {
                x: this.worldX - worldOffset,
                y: this.worldY,
                w: this.w,
                h: this.h
            };
        }
    }

    function initGame() {
        player = new Player();
        
        projectiles = [];
        keys = {};
        lastShotTime = 0;
        worldOffset = 0;
        gameActive = true;
        messageBox.style.display = 'none';
        
        const levelData = generateLevel(currentLevel);
        levelPlatforms = levelData.platforms; 
        
        enemies = levelData.enemies;
        collectibles = levelData.collectibles; 
        
        collectedObjects = 0;
        boostActive = false;
        isBossActive = currentLevel === 4; 
        screenFlashTimer = 0;
        flashOverlay.style.opacity = 0;
        flashOverlay.style.backgroundColor = 'transparent';
        
        player.score = 0;

        PLAYER_SPEED = PLAYER_SPEED_BASE * playerSpeedMultiplier;
        PROJECTILE_SPEED = PROJECTILE_SPEED_BASE * playerSpeedMultiplier;

        if (currentLevel === 2 || currentLevel === 3) {
            if (boss) {
                boss.attackState = 'ARROW_ATTACK';
                boss.laserTimer = 0;
                boss.lastArrowTime = performance.now();
            }
        }

        updateUI();
        requestAnimationFrame(gameLoop);
        console.log(`Level ${currentLevel} started. Player is invisible: ${isInvisible}`);
    }

    function drawBackground() {
        const gradient = ctx.createLinearGradient(0, 0, 0, GAME_HEIGHT);
        gradient.addColorStop(0, colors.skyTop);
        gradient.addColorStop(1, colors.skyBottom);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        drawCloud(100, 50, 60);
        drawCloud(600, 100, 80);
        drawCloud(350, 70, 50);
    }

    function drawCloud(x, y, size) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        const parts = [
            [0, 0, 1], [size * 0.4, 0, 1.2], [size * 0.7, size * 0.1, 0.9], [size * 0.2, size * 0.3, 1.1]
        ];

        ctx.beginPath();
        for (const [dx, dy, scale] of parts) {
            ctx.arc(x + dx, y + dy, size * 0.3 * scale, 0, Math.PI * 2);
        }
        ctx.fill();
    }

    function drawPlatforms() {
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.shadowOffsetY = 4;
        ctx.shadowBlur = 0;
        
        ctx.fillStyle = colors.platform;
        for (const p of levelPlatforms) {
            const screenX = p[0] - worldOffset;
            const pY = p[1];
            const pW = p[2];
            const pH = p[3];

            if (screenX + pW > 0 && screenX < GAME_WIDTH) {
                ctx.fillRect(screenX, pY, pW, pH);
            }
        }
        ctx.shadowBlur = 0;
        ctx.shadowOffsetY = 0;
    }

    function shootProjectile() {
        const now = Date.now();
        if (now - lastShotTime > SHOOT_COOLDOWN) {
            const direction = player.facingDirection; 

            const startX = player.x + (direction === 1 ? player.w : -20);
            const startY = player.y + player.h / 2 - 2; 
            projectiles.push(new Projectile(startX, startY, direction, 'fireball')); 
            lastShotTime = now;
        }
    }

    function checkCollision(objA, objB) {
        return objA.x < objB.x + objB.w &&
               objA.x + objA.w > objB.x &&
               objA.y < objB.y + objB.h &&
               objA.y + objA.h > objB.y;
    }

    function handleCollisions() {
        collectibles.forEach(c => {
            if (c.isCollected) return;
            const cScreen = c.getScreenPosition();

            if (checkCollision(player, cScreen)) {
                c.isCollected = true;
                collectedObjects++;
                updateUI();
                applyBoost();
            }
        });

        projectiles.forEach(p => {
            if (!p.isAlive) return;

            enemies.forEach(e => {
                if (!e.isAlive) return;
                const eScreen = e.getScreenPosition();

                if (checkCollision(p, eScreen)) {
                    p.isAlive = false;
                    e.isAlive = false;
                    player.score += e.scoreValue;
                    updateUI();
                }
            });

            if (isBossActive && boss && boss.isAlive) {
                const bScreen = boss.getScreenPosition();
                if (checkCollision(p, bScreen)) {
                    p.isAlive = false;
                    boss.takeDamage(p.damage); 
                    updateUI(); 
                }
            }
        });

        projectiles = projectiles.filter(p => p.isAlive);
        enemies = enemies.filter(e => e.isAlive);

        const checkDamage = (e) => {
            if (!e.isAlive || isInvisible) return; 

            const eScreen = e.getScreenPosition();
            if (checkCollision(player, eScreen)) {
                if (player.vy > 0 && player.y + player.h - 5 < eScreen.y) {
                    if (e instanceof Boss) {
                        e.takeDamage(1); 
                    } else {
                        e.isAlive = false;
                    }
                    player.vy = JUMP_POWER * 0.5; 
                    player.score += e.scoreValue;
                    updateUI();
                } else {
                    player.takeDamage();
                }
            }
        };

        enemies.forEach(checkDamage);
        if (isBossActive && boss && boss.isAlive) {
            checkDamage(boss);
        }

        if (currentLevel === 3 && isBossActive && boss && boss.isAlive && boss.attackState === 'LASER_ACTIVE') {
            const bScreenX = boss.worldX - worldOffset;
            const centerX = bScreenX + boss.w / 2;
            const centerY = boss.worldY + boss.h * 0.5;
            
            const dir = boss.laserDirection;
            
            const laserBox = {
                w: LASER_W,
                h: LASER_H,
                x: (dir === 1) ? centerX + (boss.w / 2) : centerX + (boss.w / 2) - LASER_W,
                y: centerY - LASER_H / 2
            };

            if (checkCollision(player, laserBox)) {
                player.takeDamage();
            }
        }
    }

    function updateUI() {
        const currentTotalScore = persistentScore + player.score;
        scoreDisplay.textContent = `LEVEL ${currentLevel} | SCORE: ${String(currentTotalScore).padStart(4, '0')}`;
        livesDisplay.textContent = `LIVES: ${player.lives}/${playerMaxLives} ${isInvisible ? '(INV)' : ''}`;
        objectsDisplay.textContent = `OBJECTS: ${collectedObjects}/${OBJECT_COUNT}`;
    }

    function handleBossSpawn() {
        const bossReadyToSpawn = collectedObjects >= OBJECT_COUNT && player.worldX >= BOSS_TRIGGER_X;

        if (!isBossActive && currentLevel !== 4 && bossReadyToSpawn) {
            isBossActive = true;
            boss = new Boss(BOSS_TRIGGER_X + GAME_WIDTH * 0.5, GROUND_Y - 60); 
            
            screenFlashTimer = 60; 
            console.log("MINI BOSS ENCOUNTER!");
        }

        if (screenFlashTimer > 0) {
            screenFlashTimer--;
            const color = screenFlashTimer % 10 < 5 ? '#C53030' : '#F6AD55'; 
            flashOverlay.style.backgroundColor = color;
            flashOverlay.style.opacity = (screenFlashTimer / 60) * 0.5; 
        } else {
            flashOverlay.style.opacity = 0;
            flashOverlay.style.backgroundColor = 'transparent';
        }

        if (isBossActive && boss && boss.isAlive) {
            boss.update();
        }
    }

    function gameOver(message = "GAME OVER!") {
        gameActive = false;
        
        const finalScore = persistentScore + player.score; 
        
        currentLevel = 1;
        persistentScore = 0;
        playerMaxLives = 3; 
        playerSpeedMultiplier = 1;
        playerAttackMultiplier = 1;
        isInvisible = false;
        PURCHASED_UPGRADES.health = false;
        PURCHASED_UPGRADES.speed = false;
        PURCHASED_UPGRADES.attack = false;
        
        messageBox.style.display = 'block';
        messageBox.innerHTML = `
            <p class="text-xl text-red-500">${message}</p>
            <p class="mt-3">Final Score: <span class="text-yellow-400">${finalScore}</span></p>
            <button class="control-button" id="restart-button">RESTART GAME</button>
        `;
        document.getElementById('restart-button').onclick = initGame;
    }

    function levelComplete() {
        gameActive = false;
        
        persistentScore += player.score;
        const previousLevel = currentLevel;

        if (previousLevel === 3) {
            currentLevel = 4; 
            messageBox.style.display = 'block';
            messageBox.innerHTML = `
                <p class="text-xl text-red-500">MINI BOSS DEFEATED!</p>
                <p class="mt-3">PREPARE FOR THE WORLD BOSS!</p>
                <button class="control-button" id="next-level-button">ENTER BONUS LEVEL 4</button>
            `;
            document.getElementById('next-level-button').onclick = initGame;
            return;
        }

        const nextLevel = (currentLevel % 3) + 1;
        currentLevel = nextLevel;
        
        isInvisible = false;

        messageBox.style.display = 'block';
        messageBox.innerHTML = `
            <p class="text-xl text-yellow-400">LEVEL ${previousLevel} COMPLETE!</p>
            <p class="mt-3">Total Score: <span class="text-yellow-400">${persistentScore}</span></p>
            <button class="control-button" id="next-level-button">ADVANCE TO LEVEL ${currentLevel}</button>
        `;
        document.getElementById('next-level-button').onclick = initGame;
    }

    function showShopScreen() {
        gameActive = false;
        
        persistentScore += player.score;
        player.score = 0;
        
        isInvisible = false; 
        
        let shopHTML = `
            <p class="text-xl text-yellow-400 mb-2 font-bold">WORLD BOSS DEFEATED! REWARD SHOP</p>
            <p class="mb-2 text-xs">Current Points: <span id="current-points" class="text-yellow-400">${persistentScore}</span></p>

            <h3 class="text-sm mt-2 mb-1 text-green-400">POWER-UP EXCHANGE:</h3>
            <div class="space-y-1 mb-2 text-left">
                <button id="buy-health" data-price="${PRICE_HEALTH}" data-upgrade="health" class="buy-button control-button w-full ${PURCHASED_UPGRADES.health ? 'bought' : ''}">
                    +2 Lives (${PRICE_HEALTH} pts)
                </button>
                <button id="buy-speed" data-price="${PRICE_SPEED}" data-upgrade="speed" class="buy-button control-button w-full ${PURCHASED_UPGRADES.speed ? 'bought' : ''}">
                    x2 Speed (${PRICE_SPEED} pts)
                </button>
                <button id="buy-attack" data-price="${PRICE_ATTACK}" data-upgrade="attack" class="buy-button control-button w-full ${PURCHASED_UPGRADES.attack ? 'bought' : ''}">
                    +50% Dmg (${PRICE_ATTACK} pts)
                </button>
            </div>
            
            <h3 class="text-sm mb-1 text-red-500">HIGH-RISK DICE ROLL:</h3>
            <p id="dice-status" class="text-xs italic mb-2">Roll 3 dice for a chance at INVISIBILITY.</p>
            <button id="roll-dice" class="control-button bg-red-600 hover:bg-red-700 w-full" data-rolled="false">
                ROLL 🎲 (Once)
            </button>
            <p id="roll-result" class="text-sm font-bold mt-1"></p>
            <p id="roll-message" class="text-xs mt-1"></p>
            
            <button class="control-button mt-4 bg-green-500 hover:bg-green-600" id="continue-game">
                CONTINUE TO WORLD 1
            </button>
        `;

        messageBox.style.display = 'block';
        messageBox.innerHTML = shopHTML;
        
        document.querySelectorAll('.buy-button').forEach(button => {
            if (!button.classList.contains('bought')) {
                button.addEventListener('click', handlePurchase);
            }
        });
        
        document.getElementById('roll-dice').addEventListener('click', handleDiceRoll);
        document.getElementById('continue-game').addEventListener('click', continueGame);
    }

    function handlePurchase(event) {
        const button = event.target;
        const price = parseInt(button.dataset.price);
        const upgrade = button.dataset.upgrade;
        
        if (persistentScore < price) {
            showMessage("Not enough points! Need " + price + " pts.");
            return;
        }

        persistentScore -= price;
        
        switch (upgrade) {
            case 'health':
                playerMaxLives += 2;
                PURCHASED_UPGRADES.health = true;
                break;
            case 'speed':
                playerSpeedMultiplier += 1; 
                break;
            case 'attack':
                playerAttackMultiplier += 0.5; 
                break;
        }
        
        document.getElementById('current-points').textContent = persistentScore;
        button.textContent += " (BOUGHT)";
        button.classList.add('bought');
        button.disabled = true;
        button.removeEventListener('click', handlePurchase);
        
        console.log(`Purchased ${upgrade}. New Max Lives: ${playerMaxLives}, Speed Mult: ${playerSpeedMultiplier}, Attack Mult: ${playerAttackMultiplier.toFixed(1)}`);
    }

    function handleDiceRoll() {
        const rollDiceButton = document.getElementById('roll-dice');
        if (rollDiceButton.dataset.rolled === 'true') return;
        
        rollDiceButton.dataset.rolled = 'true';
        rollDiceButton.textContent = "ROLLED";
        rollDiceButton.classList.add('bought');

        const d1 = Math.floor(Math.random() * 6) + 1;
        const d2 = Math.floor(Math.random() * 6) + 1;
        const d3 = Math.floor(Math.random() * 6) + 1;
        const total = d1 + d2 + d3;

        let message;
        
        if (total >= 15) {
            isInvisible = true;
            message = `<span class="text-green-400">SUCCESS! Total ${total}.</span> You are **INVISIBLE** for the next world!`;
        } 
        else if (total <= 5) {
            playerMaxLives = 3;
            playerSpeedMultiplier = 1;
            playerAttackMultiplier = 1;
            persistentScore = 0;
            PURCHASED_UPGRADES.health = false;
            PURCHASED_UPGRADES.speed = false;
            PURCHASED_UPGRADES.attack = false;
            
            document.querySelectorAll('.buy-button').forEach(btn => {
                btn.classList.remove('bought');
                btn.disabled = false;
                btn.textContent = btn.textContent.replace(' (BOUGHT)', '');
                btn.addEventListener('click', handlePurchase);
            });

            message = `<span class="text-red-500">CRITICAL FAILURE! Total ${total}.</span> All upgrades and points lost! Stats reverted.`;
        } 
        else {
            message = `<span class="text-yellow-400">NEUTRAL. Total ${total}.</span> Nothing gained, nothing lost.`;
        }

        document.getElementById('roll-result').innerHTML = `Rolls: ${d1} | ${d2} | ${d3} (Total: ${total})`;
        document.getElementById('roll-message').innerHTML = message;
        document.getElementById('current-points').textContent = persistentScore; 
    }

    function continueGame() {
        currentLevel = 1;
        messageBox.style.display = 'none';
        initGame(); 
    }
    
    function showMessage(text, callback = null) {
        const tempBox = document.createElement('div');
        tempBox.id = 'temp-message-box';
        tempBox.className = 'fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-black bg-opacity-90 p-4 border-2 border-yellow-400 text-white text-sm z-50 rounded-lg shadow-xl';
        tempBox.textContent = text;
        document.body.appendChild(tempBox);

        setTimeout(() => {
            tempBox.remove();
            if (callback) callback();
        }, 1500); 
    }

    function gameLoop() {
        if (!gameActive) return;

        drawBackground();
        drawPlatforms();

        player.update();
        enemies.forEach(e => e.update());
        projectiles.forEach(p => p.update());
        handleBossSpawn();

        handleCollisions();

        collectibles.forEach(c => {
             const screenX = c.worldX - worldOffset;
             if (screenX + c.w > 0 && screenX < GAME_WIDTH) {
                 c.draw();
             }
        });
        
        enemies.forEach(e => {
            const screenX = e.worldX - worldOffset;
            if (screenX + e.w > 0 && screenX < GAME_WIDTH) {
                e.draw();
            }
        });
        
        if (isBossActive && boss && boss.isAlive) {
             const screenX = boss.worldX - worldOffset;
             if (screenX + boss.w > 0 && screenX < GAME_WIDTH) {
                 boss.draw();
             }
        }

        player.draw();
        projectiles.forEach(p => p.draw());

        requestAnimationFrame(gameLoop);
    }

    document.addEventListener('keydown', (e) => {
        if (!gameActive) return;

        const key = e.key;
        keys[key] = true;

        if (key === 'ArrowUp') {
            e.preventDefault(); 
            player.jump();
        }
        
        if (key === ' ') {
            e.preventDefault(); 
            shootProjectile();
        }
        
        if (key.startsWith('Arrow')) {
             e.preventDefault();
        }
    });

    document.addEventListener('keyup', (e) => {
        keys[e.key] = false;
    });

    startButton.onclick = initGame;

    const mobileControls = document.getElementById('mobile-controls');
    
    const createMobileButton = (text, key) => {
        const button = document.createElement('button');
        button.className = 'control-button';
        button.textContent = text;
        button.ontouchstart = (e) => {
            e.preventDefault();
            keys[key] = true;
            if (key === 'ArrowUp') player.jump();
            if (key === ' ') shootProjectile();
        };
        button.ontouchend = (e) => {
            e.preventDefault();
            keys[key] = false;
        };
        return button;
    };
    
    mobileControls.appendChild(createMobileButton('◀️', 'ArrowLeft'));
    mobileControls.appendChild(createMobileButton('JUMP (↑)', 'ArrowUp'));
    mobileControls.appendChild(createMobileButton('SHOOT', ' '));
    mobileControls.appendChild(createMobileButton('▶️', 'ArrowRight'));


</script>
</body>
</html>
"""

# 4. Render the Game Component
# Increased height to 600px to ensure the Shop/Dice modal doesn't get cut off.
components.html(game_html, height=600, scrolling=False)
