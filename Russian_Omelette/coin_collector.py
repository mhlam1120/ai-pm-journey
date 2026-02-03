import streamlit as st
import streamlit.components.v1 as components

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Russian Omelette",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Header ---
st.title("🍳 Russian Omelette")

# --- Game Logic (HTML/JS Embedding) ---
# We bundle the entire game engine (originally React) into a single HTML string
# to run efficiently in the browser via Streamlit's component API.

game_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Russian Omelette</title>
    <style>
        body {
            margin: 0;
            background-color: #0e1117; /* Streamlit dark bg match */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            user-select: none;
            overflow: hidden;
            touch-action: none;
        }
        #game-container {
            position: relative;
            width: 600px;
            max-width: 100%;
            aspect-ratio: 4/3;
            border: 4px solid #444;
            border-radius: 8px;
            overflow: hidden;
            background: #000;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        canvas {
            display: block;
            width: 100%;
            height: 100%;
            image-rendering: pixelated; /* Retro look */
        }
        #ui-layer {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 10px 20px;
            box-sizing: border-box;
            display: flex;
            justify-content: space-between;
            pointer-events: none;
            text-shadow: 2px 2px 0 #000;
        }
        .stat-box {
            background: rgba(0, 0, 0, 0.6);
            padding: 5px 15px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            font-weight: bold;
            font-size: 16px;
            text-shadow: 1px 1px 0 #000;
        }
        #score-display { color: #FFD700; }
        #level-display { color: #87CEFA; }
        
        /* Start Screen / Leaderboard */
        #start-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 20, 30, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 20;
        }
        
        /* Leaderboard Container */
        #leaderboard-container {
            width: 90%;
            height: 200px;
            overflow-y: auto;
            position: relative;
            border: 1px solid #444;
            border-radius: 4px;
            background: rgba(0,0,0,0.3);
        }

        /* Custom Scrollbar for Leaderboard */
        #leaderboard-container::-webkit-scrollbar {
            width: 8px;
        }
        #leaderboard-container::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.3); 
            border-radius: 4px;
        }
        #leaderboard-container::-webkit-scrollbar-thumb {
            background: #555; 
            border-radius: 4px;
        }
        #leaderboard-container::-webkit-scrollbar-thumb:hover {
            background: #87CEFA; 
        }

        table { border-collapse: collapse; width: 90%; margin: 0 auto; color: #ddd; font-size: 13px; }
        th, td { border-bottom: 1px solid #444; padding: 8px; text-align: left; }
        th { color: #87CEFA; background: #111; position: sticky; top: 0; }
        
        /* Help Screen Overlay */
        #help-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 30;
            padding: 20px;
            box-sizing: border-box;
        }
        #help-screen h2 { color: #FFD700; margin-bottom: 20px; }
        #help-screen ul { list-style: none; padding: 0; text-align: left; max-width: 400px; }
        #help-screen li { margin-bottom: 12px; font-size: 16px; color: #eee; line-height: 1.4; }
        
        /* Game Over Overlay */
        #game-over-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }
        h1 { margin: 0 0 10px 0; font-size: 48px; color: #ff4444; font-family: monospace; text-shadow: 3px 3px 0 #000; }
        p { font-size: 24px; margin-bottom: 20px; font-family: monospace; }
        
        input[type="text"] {
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #555;
            background: #222;
            color: white;
            font-size: 18px;
            margin-bottom: 15px;
            width: 200px;
            text-align: center;
            font-family: monospace;
        }

        .btn-green {
            padding: 12px 30px;
            font-size: 18px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-family: monospace;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 4px 0 #1e7e34;
            transition: transform 0.1s;
        }
        .btn-green:hover { background: #218838; }
        .btn-green:active { transform: translateY(4px); box-shadow: 0 0 0 #1e7e34; }

        /* Level Transition Overlay */
        #level-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9;
        }
        .level-text { font-size: 40px; color: #32CD32; font-weight: bold; font-family: monospace; text-shadow: 2px 2px 0 #000; animation: bounce 1s infinite; }

        /* Touch Controls */
        #controls-area {
            width: 600px;
            max-width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            box-sizing: border-box;
            margin-top: 10px;
        }
        .control-group { display: flex; gap: 15px; }
        .touch-btn {
            width: 60px;
            height: 60px;
            background: #333;
            border: 2px solid #555;
            border-radius: 12px;
            color: white;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            user-select: none;
            box-shadow: 0 4px 0 #111;
            -webkit-tap-highlight-color: transparent;
        }
        .touch-btn:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #111;
        }
        .btn-red { background: #d32f2f; border-color: #b71c1c; box-shadow: 0 4px 0 #b71c1c; }
        .btn-blue { background: #1976d2; border-color: #0d47a1; box-shadow: 0 4px 0 #0d47a1; }
        .btn-help, .btn-sound { width: 40px; height: 40px; font-size: 20px; background: #444; }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div id="ui-layer">
            <div id="score-display" class="stat-box">Score: 0</div>
            <div id="level-display" class="stat-box">Level 1 • Coins Left: 0</div>
        </div>

        <!-- Help Screen -->
        <div id="help-screen">
            <h2>HOW TO PLAY</h2>
            <ul>
                <li><b>Desktop:</b> Arrow Keys to Move/Jump, Spacebar to Attack.</li>
                <li><b>Mobile:</b> Use the on-screen buttons below.</li>
                <li><b>Goal:</b> Collect coins to open the next level.</li>
                <li><b>Warning:</b> One coin per level is <span style="color:#FF4500; font-weight:bold;">ROTTEN</span>! Collecting it turns you into an <b>Egg</b>.</li>
                <li><b>Egg Mode:</b> The floor disappears! Roll on platforms to survive.</li>
                <li><b>Lightning:</b> If you have <span style="color:#FFFF00;">3+ Rotten Eggs</span>, moving stops causing <b>Lightning Strike</b>! (>3 eggs = Extreme Speed)</li>
            </ul>
            <button class="btn-green" style="margin-top:20px;" onclick="toggleHelp()">Close</button>
        </div>

        <!-- Start Screen / Leaderboard -->
        <div id="start-screen">
            <h1 style="color:#32CD32; margin-bottom: 5px; text-shadow: 4px 4px 0 #000; font-family: monospace; font-size: 50px;">RUSSIAN OMELETTE</h1>
            <h4 style="margin-top: 0; margin-bottom: 15px; color: #87CEFA; font-style: italic; font-family: monospace;">Design & Created by Timothy Lam</h4>
            <h3 style="margin-top: 0; margin-bottom: 10px; color: #aaa;">🏆 TOP 10 PLAYERS 🏆</h3>
            
            <!-- Fixed Header Table -->
            <table style="width: 90%; margin-bottom: 0;">
                <thead><tr><th style="width:15%">Rank</th><th style="width:30%">Name</th><th style="width:15%">Lvl</th><th style="width:15%">Score</th><th style="width:25%">Death</th></tr></thead>
            </table>
            
            <!-- Scrolling Body Container -->
            <div id="leaderboard-container">
                <table id="leaderboard-table" style="margin-top: 0;">
                    <tbody id="leaderboard-body"></tbody>
                </table>
            </div>
            
            <button class="btn-green" style="margin-top: 20px;" onclick="startGame()">Start Game</button>
        </div>

        <div id="level-screen">
            <div class="level-text">LEVEL COMPLETE!</div>
            <div style="margin-top:10px; color:#ddd; font-family: monospace;">Next Area Loading...</div>
        </div>

        <!-- Game Over Screen -->
        <div id="game-over-screen">
            <h1 id="game-over-title">GAME OVER</h1>
            <p id="final-stats">Level Reached: 1 | Score: 0</p>
            
            <!-- High Score Entry -->
            <div id="high-score-area" style="display:none; flex-direction:column; align-items:center;">
                <p style="color:#FFD700; margin-top:0; font-weight:bold; font-family: monospace;">🎉 NEW HIGH SCORE! 🎉</p>
                <input type="text" id="player-name" placeholder="ENTER NAME" maxlength="12">
                <button class="btn-green" onclick="submitScore()">SAVE SCORE</button>
            </div>

            <!-- Standard Restart -->
            <div id="no-high-score-area" style="display:none; flex-direction:column; align-items:center;">
                <button class="btn-green" onclick="resetGame()">TRY AGAIN</button>
            </div>
        </div>
    </div>

    <!-- Mobile/Touch Controls -->
    <div id="controls-area">
        <div class="control-group">
            <div class="touch-btn" id="btn-left">←</div>
            <div class="touch-btn" id="btn-right">→</div>
        </div>
        
        <div style="display:flex; gap:10px;">
            <div class="touch-btn btn-sound" id="btn-sound" onclick="toggleMute()">🔊</div>
            <div class="touch-btn btn-help" onclick="toggleHelp()">?</div>
        </div>

        <div class="control-group">
            <div class="touch-btn btn-red" id="btn-attack">⚔️</div>
            <div class="touch-btn btn-blue" id="btn-jump">↑</div>
        </div>
    </div>

<script>
    // --- Constants ---
    const LOGICAL_WIDTH = 800;
    const LOGICAL_HEIGHT = 600;
    const GRAVITY = 0.55;
    const PLAYER_SPEED = 5;
    const JUMP_STRENGTH = -13.5;
    const ENEMY_SPEED_BASE = 1;

    // --- Sound Manager (Web Audio API) ---
    const Sound = {
        ctx: null, gainNode: null, isMuted: false, musicInterval: null,
        init: function() {
            if (!this.ctx) {
                const AC = window.AudioContext || window.webkitAudioContext;
                this.ctx = new AC();
                this.gainNode = this.ctx.createGain();
                this.gainNode.connect(this.ctx.destination);
                this.gainNode.gain.value = 0.1; // Master volume
            }
            if (this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
            this.startMusic();
        },

        toggle: function() {
            this.isMuted = !this.isMuted;
            const btn = document.getElementById('btn-sound');
            if (this.isMuted) {
                if (this.gainNode) this.gainNode.gain.value = 0;
                btn.innerText = "🔇";
                this.stopMusic();
            } else {
                if (this.gainNode) this.gainNode.gain.value = 0.1;
                btn.innerText = "🔊";
                this.startMusic();
            }
        },

        playTone: function(freq, type, duration, vol=1) {
            if (this.isMuted || !this.ctx) return;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            gain.gain.setValueAtTime(vol, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);
            osc.connect(this.gainNode); 
            osc.connect(gain);
            gain.connect(this.gainNode);
            
            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        },

        playNoise: function(duration) {
            if (this.isMuted || !this.ctx) return;
            const bufferSize = this.ctx.sampleRate * duration;
            const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }
            const noise = this.ctx.createBufferSource();
            noise.buffer = buffer;
            const gain = this.ctx.createGain();
            gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);
            noise.connect(gain);
            gain.connect(this.gainNode);
            noise.start();
        },

        jump: function() { this.playTone(300, 'square', 0.1); },
        attack: function() { this.playNoise(0.1); },
        hit: function() { this.playTone(150, 'square', 0.1); },
        coin: function() { 
            this.playTone(1200, 'sine', 0.1, 0.5); 
            setTimeout(() => this.playTone(1600, 'sine', 0.2, 0.5), 100);
        },
        rotten: function() {
            this.playTone(150, 'sawtooth', 0.5);
            this.playTone(100, 'sawtooth', 0.5);
        },
        splash: function() { 
            this.playNoise(0.4); 
            if (this.isMuted || !this.ctx) return;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.frequency.setValueAtTime(400, this.ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(50, this.ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 0.3);
            osc.connect(gain);
            gain.connect(this.gainNode);
            osc.start();
            osc.stop(this.ctx.currentTime + 0.3);
        },
        lightning: function() { 
            this.playNoise(0.5); 
            this.playTone(800, 'sawtooth', 0.1, 0.5);
            this.playTone(100, 'square', 0.6, 0.5);
        },
        death: function() {
            this.playTone(200, 'sawtooth', 0.5);
            setTimeout(() => this.playTone(100, 'sawtooth', 0.8), 200);
        },
        
        startMusic: function() {
            if (this.musicInterval || this.isMuted) return;
            let n = 0;
            const notes = [261, 311, 392, 523, 392, 311];
            this.musicInterval = setInterval(() => {
                if(this.isMuted) return;
                this.playTone(notes[n%notes.length], 'triangle', 0.2, 0.03);
                n++;
            }, 300);
        },
        
        stopMusic: function() {
            if (this.musicInterval) {
                clearInterval(this.musicInterval);
                this.musicInterval = null;
            }
        }
    };

    // --- Fixed Level Layouts ---
    const LEVEL_LAYOUTS = [
      [ { x: 0, y: 580, width: 800, height: 20 }, { x: 50, y: 480, width: 100, height: 20 }, { x: 200, y: 400, width: 100, height: 20 }, { x: 350, y: 320, width: 100, height: 20 }, { x: 500, y: 240, width: 100, height: 20 }, { x: 650, y: 160, width: 100, height: 20 }, { x: 400, y: 100, width: 150, height: 20 } ],
      [ { x: 0, y: 580, width: 800, height: 20 }, { x: 100, y: 450, width: 80, height: 20 }, { x: 100, y: 350, width: 80, height: 20 }, { x: 100, y: 250, width: 80, height: 20 }, { x: 600, y: 450, width: 80, height: 20 }, { x: 600, y: 350, width: 80, height: 20 }, { x: 600, y: 250, width: 80, height: 20 }, { x: 350, y: 150, width: 100, height: 20 } ],
      [ { x: 0, y: 580, width: 800, height: 20 }, { x: 50, y: 500, width: 100, height: 20 }, { x: 650, y: 500, width: 100, height: 20 }, { x: 150, y: 400, width: 100, height: 20 }, { x: 550, y: 400, width: 100, height: 20 }, { x: 250, y: 300, width: 100, height: 20 }, { x: 450, y: 300, width: 100, height: 20 }, { x: 350, y: 180, width: 100, height: 20 } ],
      [ { x: 0, y: 580, width: 800, height: 20 }, { x: 50, y: 450, width: 80, height: 20 }, { x: 200, y: 350, width: 80, height: 20 }, { x: 50, y: 250, width: 80, height: 20 }, { x: 400, y: 250, width: 80, height: 20 }, { x: 650, y: 450, width: 80, height: 20 }, { x: 500, y: 350, width: 80, height: 20 }, { x: 650, y: 250, width: 80, height: 20 } ],
      [ { x: 0, y: 580, width: 800, height: 20 }, { x: 350, y: 500, width: 100, height: 20 }, { x: 150, y: 400, width: 80, height: 20 }, { x: 550, y: 400, width: 80, height: 20 }, { x: 50, y: 300, width: 80, height: 20 }, { x: 650, y: 300, width: 80, height: 20 }, { x: 250, y: 200, width: 300, height: 20 } ]
    ];

    let canvas, ctx;
    let gameState = {
        player: { x: 50, y: 500, width: 40, height: 40, vx: 0, vy: 0, onGround: false, jumpCount: 0, maxJumps: 2, isAttacking: false, attackTimer: 0, facing: 'right', isHumpty: false, rotation: 0, stationaryTimer: 0 },
        keys: { left: false, right: false, up: false, space: false },
        platforms: [], coins: [], enemies: [], clouds: [], particles: [], wind: [], meteors: [],
        level: 1, score: 0, coinsCollected: 0, totalCoins: 0, eggsCollected: 0,
        gameOver: false, transition: false, splash: { active: false, timer: 0, x: 0, y: 0 }, lightning: { active: false, timer: 0, x: 0, y: 0 },
        isMenu: true, isPaused: false, deathReason: null, levelTimer: null
    };

    window.onload = function() {
        canvas = document.getElementById('gameCanvas');
        ctx = canvas.getContext('2d');
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);
        setupTouchControls();
        renderLeaderboard();
        
        // Init Background stars/mountains
        for(let i=0; i<30; i++) gameState.clouds.push({x:Math.random()*LOGICAL_WIDTH, y:Math.random()*200, type:'star', s:Math.random()*2});
        for(let i=0; i<5; i++) gameState.clouds.push({x:Math.random()*LOGICAL_WIDTH, y:Math.random()*150, type:'cloud', s:0.5+Math.random()*0.5, v:0.2+Math.random()*0.3});
        
        requestAnimationFrame(gameLoop);
    };

    function createParticle(x, y, color, speed=2) {
        for(let i=0; i<5; i++) {
            gameState.particles.push({
                x: x, y: y,
                vx: (Math.random()-0.5)*speed, vy: (Math.random()-0.5)*speed,
                life: 30, color: color, size: Math.random()*4+2
            });
        }
    }

    function getLeaderboard() { const s = localStorage.getItem('ninja_leaderboard'); return s ? JSON.parse(s) : []; }
    function saveLeaderboard(d) { localStorage.setItem('ninja_leaderboard', JSON.stringify(d)); }
    function renderLeaderboard() {
        const data = getLeaderboard();
        const tbody = document.getElementById('leaderboard-body');
        tbody.innerHTML = '';
        if (data.length===0) { tbody.innerHTML='<tr><td colspan="5" style="text-align:center;">No records yet!</td></tr>'; return; }
        data.forEach((e,i) => {
            let r=i+1; if(i===0)r='🥇';if(i===1)r='🥈';if(i===2)r='🥉';
            tbody.innerHTML += `<tr><td>${r}</td><td style="color:#fff;font-weight:bold;">${e.name}</td><td>${e.level}</td><td>${e.score}</td><td style="font-size:11px;color:#aaa;">${e.death||'-'}</td></tr>`;
        });
    }

    function toggleHelp() {
        const el = document.getElementById('help-screen');
        const show = el.style.display !== 'flex';
        el.style.display = show ? 'flex' : 'none';
        gameState.isPaused = show;
    }
    function toggleMute() { Sound.toggle(); }

    function startGame() {
        Sound.init();
        document.getElementById('start-screen').style.display = 'none';
        gameState.isMenu = false; gameState.score = 0; gameState.gameOver = false;
        gameState.deathReason = null; gameState.eggsCollected = 0;
        startNewLevel(1);
    }

    function startNewLevel(lvl, keep=false) {
        const idx = (lvl-1) % LEVEL_LAYOUTS.length;
        const layout = JSON.parse(JSON.stringify(LEVEL_LAYOUTS[idx]));
        gameState.platforms = layout;
        gameState.coins = []; gameState.enemies = []; gameState.particles = []; gameState.wind = []; gameState.meteors = [];
        gameState.level = lvl; gameState.coinsCollected = 0; gameState.transition = false;
        gameState.splash.active = false; gameState.lightning = {active:false, timer:0};
        gameState.player.stationaryTimer = 0;
        if(gameState.levelTimer) clearTimeout(gameState.levelTimer);

        if(!keep) {
            gameState.player.x = 50; gameState.player.y = 500; gameState.player.vx=0; gameState.player.vy=0;
            gameState.player.isHumpty = false;
        }
        
        // Wind Gust Trigger on specific levels (3, 5, 7...)
        if (lvl > 1 && lvl % 2 !== 0) {
            setTimeout(() => {
                gameState.wind.push({ x: -100, y: 0, width: 40, height: LOGICAL_HEIGHT, vx: 8, active: true });
            }, 1000);
        }
        
        // Meteors every 5 levels
        if (lvl % 5 === 0) {
            gameState.levelTimer = setTimeout(() => {
                for(let i=0; i<8; i++) {
                    gameState.meteors.push({
                        x: Math.random() * LOGICAL_WIDTH,
                        y: -50 - (Math.random() * 300),
                        width: 30, height: 30,
                        vx: (Math.random() - 0.5) * 2,
                        vy: 4 + Math.random() * 4,
                        active: true,
                        rotation: 0
                    });
                }
            }, 5000);
        }

        const tCoins = 5 + (lvl-1);
        const cPlats = gameState.platforms.filter(p => p.y < 550);
        for(let i=cPlats.length-1; i>0; i--) { const j=Math.floor(Math.random()*(i+1)); [cPlats[i],cPlats[j]]=[cPlats[j],cPlats[i]]; }
        
        let p=0, k=0;
        while(p < tCoins && cPlats.length>0) {
            const plat = cPlats[k%cPlats.length];
            gameState.coins.push({ x: plat.x+Math.random()*(plat.width-20)+5, y: plat.y-30, width:20, height:20, active:true, float:Math.random()*6, type:'real' });
            p++; k++;
        }
        if(gameState.coins.length>0) gameState.coins[Math.floor(Math.random()*gameState.coins.length)].type = 'fake';
        gameState.totalCoins = gameState.coins.filter(c=>c.type==='real').length;

        const eCount = Math.min(lvl+1, 6);
        for(let i=0; i<eCount; i++) {
            gameState.enemies.push({ x: Math.random()*(LOGICAL_WIDTH-250)+200, y: 540, width:35, height:35, vx:0, speed:ENEMY_SPEED_BASE+(lvl*0.25), active:true, bounce: Math.random()*10 });
        }
        updateUI();
        document.getElementById('level-screen').style.display = 'none';
        document.getElementById('game-over-title').innerText = "GAME OVER";
        document.getElementById('game-over-title').style.color = "#ff4444";
    }

    function resetGame() {
        gameState.score = 0; gameState.gameOver = false; gameState.deathReason = null;
        gameState.eggsCollected = 0; gameState.player.isHumpty = false;
        document.getElementById('game-over-screen').style.display = 'none';
        startNewLevel(1);
    }

    function submitScore() {
        const name = document.getElementById('player-name').value.trim() || "Ninja";
        const lb = getLeaderboard();
        lb.push({name:name, level:gameState.level, score:gameState.score, death:gameState.deathReason});
        lb.sort((a,b) => (b.level!==a.level ? b.level-a.level : b.score-a.score));
        saveLeaderboard(lb.slice(0,10));
        document.getElementById('game-over-screen').style.display = 'none';
        document.getElementById('start-screen').style.display = 'flex';
        renderLeaderboard();
        gameState.isMenu = true;
    }

    function handleKeyDown(e) {
        if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Space'].includes(e.code)) e.preventDefault();
        if(gameState.isMenu) return;
        if(e.code==='ArrowLeft') gameState.keys.left=true;
        if(e.code==='ArrowRight') gameState.keys.right=true;
        if(e.code==='ArrowUp') { if(!gameState.keys.up) performJump(); gameState.keys.up=true; }
        if(e.code==='Space') { gameState.keys.space=true; performAttack(); }
        if(e.code==='KeyR' && gameState.gameOver) resetGame();
    }
    function handleKeyUp(e) {
        if(e.code==='ArrowLeft') gameState.keys.left=false;
        if(e.code==='ArrowRight') gameState.keys.right=false;
        if(e.code==='ArrowUp') gameState.keys.up=false;
        if(e.code==='Space') gameState.keys.space=false;
    }
    function setupTouchControls() {
        const bind = (id,k,act) => {
            const b = document.getElementById(id);
            const down = (e) => { e.preventDefault(); if(gameState.isMenu)return; gameState.keys[k]=true; b.classList.add('pressed'); if(act)act(); };
            const up = (e) => { e.preventDefault(); gameState.keys[k]=false; b.classList.remove('pressed'); };
            b.addEventListener('touchstart', down); b.addEventListener('touchend', up);
            b.addEventListener('mousedown', down); b.addEventListener('mouseup', up); b.addEventListener('mouseleave', up);
        };
        bind('btn-left','left'); bind('btn-right','right');
        bind('btn-jump','up',performJump); bind('btn-attack','space',performAttack);
    }

    function performJump() {
        if(gameState.gameOver||gameState.transition||gameState.isMenu||gameState.isPaused) return;
        const p = gameState.player;
        if(p.jumpCount < p.maxJumps) {
            p.vy = JUMP_STRENGTH; p.jumpCount++; p.onGround = false;
            Sound.jump(); createParticle(p.x+20, p.y+40, '#fff', 3);
        }
    }
    function performAttack() {
        if(gameState.gameOver||gameState.transition||gameState.isMenu||gameState.isPaused||gameState.player.isHumpty) return;
        const p = gameState.player;
        if(p.attackTimer===0) { p.isAttacking=true; p.attackTimer=20; Sound.attack(); }
    }
    function checkCol(r1, r2) { return r1.x<r2.x+r2.width && r1.x+r1.width>r2.x && r1.y<r2.y+r2.height && r1.y+r1.height>r2.y; }

    function update() {
        if(gameState.isMenu||gameState.isPaused) return;
        if(gameState.gameOver && !gameState.splash.active && !gameState.lightning.active) return;
        if(gameState.transition) return;

        const p = gameState.player;

        // Particles
        for(let i=gameState.particles.length-1; i>=0; i--) {
            let pt = gameState.particles[i];
            pt.x += pt.vx; pt.y += pt.vy; pt.life--;
            if(pt.life<=0) gameState.particles.splice(i,1);
        }

        // Background
        gameState.clouds.forEach(c => {
            if(c.type==='cloud') { c.x-=c.v; if(c.x<-100) c.x=LOGICAL_WIDTH+100; }
        });
        
        // Wind
        gameState.wind.forEach(w => {
            if(!w.active) return;
            w.x += w.vx;
            if(w.x > LOGICAL_WIDTH) w.active = false;
            gameState.coins.forEach(c => {
                if(c.active && checkCol(w, c)) {
                    const randPlat = gameState.platforms[Math.floor(Math.random() * gameState.platforms.length)];
                    c.x = randPlat.x + Math.random() * (randPlat.width - 20);
                    c.y = randPlat.y - 30;
                    c.float = Math.random() * 6;
                }
            });
        });
        
        // Meteors
        gameState.meteors.forEach(m => {
            if(!m.active) return;
            m.x += m.vx; m.y += m.vy; m.rotation += 0.1;
            if(checkCol(p, m)) {
                gameState.deathReason = "Crushed by Meteor ☄️"; gameState.gameOver = true; Sound.death(); showGameOver();
            }
            if(m.y > LOGICAL_HEIGHT) m.active = false;
        });

        // Player Physics
        if(p.isHumpty) {
            // Egg Logic
            if(gameState.eggsCollected >= 3) {
                if(Math.abs(p.vx)<0.3 && Math.abs(p.vy)<0.3) p.stationaryTimer++; else p.stationaryTimer=0;
                if(p.stationaryTimer > 180) { triggerLightning(p); return; }
            } else p.stationaryTimer=0;

            let acc = 0.2, fric = 0.98, max = 6;
            if(gameState.eggsCollected > 3) { acc=0.5; fric=0.995; max=12; }
            if(gameState.keys.left) p.vx -= acc;
            if(gameState.keys.right) p.vx += acc;
            p.vx *= fric;
            if(p.vx > max) p.vx=max; if(p.vx < -max) p.vx=-max;
            p.x += p.vx; p.vy += GRAVITY; p.y += p.vy;
            p.rotation += p.vx*0.1;
        } else {
            // Ninja Logic
            if(gameState.keys.left) { p.x-=PLAYER_SPEED; p.facing='left'; }
            if(gameState.keys.right) { p.x+=PLAYER_SPEED; p.facing='right'; }
            p.vy += GRAVITY; p.y += p.vy;
            // Running dust
            if(p.onGround && (gameState.keys.left || gameState.keys.right) && Math.random()>0.8) {
                createParticle(p.x+20, p.y+40, '#888', 1);
            }
        }

        // Bounds
        if(p.x < 0) { p.x=0; if(p.isHumpty)p.vx*=-0.5; }
        if(p.x+p.width > LOGICAL_WIDTH) { p.x=LOGICAL_WIDTH-p.width; if(p.isHumpty)p.vx*=-0.5; }
        if(p.attackTimer>0) p.attackTimer--; else p.isAttacking=false;

        // Platforms
        p.onGround = false;
        gameState.platforms.forEach(plat => {
            if(p.isHumpty && plat.y >= 580 && plat.width >= 800) return; // Egg falls thru ground
            if(checkCol(p, plat)) {
                if(p.vy > 0 && (p.y+p.height-p.vy) <= plat.y) {
                    p.y = plat.y - p.height; p.vy = 0; p.onGround = true; p.jumpCount = 0;
                    if(p.vy > 5) Sound.land(); // Heavy landing
                }
                else if(p.vy < 0 && (p.y-p.vy) >= plat.y+plat.height) { p.y = plat.y+plat.height; p.vy = 0; }
            }
        });

        // Floor Death
        if(p.y+p.height > LOGICAL_HEIGHT) {
            if(p.isHumpty) triggerSplash(p);
            else { p.y = LOGICAL_HEIGHT-p.height; p.vy = 0; p.onGround = true; p.jumpCount = 0; }
        }

        // Coins
        let collected = false;
        gameState.coins.forEach(c => {
            if(!c.active) return;
            c.float += 0.1;
            if(checkCol(p, c)) {
                c.active = false;
                createParticle(c.x+10, c.y+10, '#FFD700', 4);
                if(c.type === 'fake') {
                    p.isHumpty = true; p.isAttacking = false; p.vy = -5;
                    gameState.eggsCollected++; Sound.rotten();
                } else {
                    gameState.score++; gameState.coinsCollected++; collected = true; Sound.coin();
                }
            }
        });
        if(collected) updateUI();

        // Level Up
        if(gameState.coinsCollected >= gameState.totalCoins && !gameState.transition) {
            gameState.transition = true;
            document.getElementById('level-screen').style.display = 'flex';
            setTimeout(() => startNewLevel(gameState.level+1, false), 1500);
        }

        // Enemies
        gameState.enemies.forEach(e => {
            if(!e.active) return;
            e.bounce += 0.1;
            if(e.x < p.x) e.x += e.speed; else e.x -= e.speed;
            if(e.y+e.height < LOGICAL_HEIGHT) e.y += 5;

            let hit = false;
            if(p.isAttacking) {
                const reach = 50;
                const box = { x: p.facing==='right'?p.x:p.x-reach, y:p.y, width:p.width+reach, height:p.height };
                if(checkCol(box, e)) hit = true;
            }

            if(hit) {
                e.active = false; gameState.score++; updateUI(); Sound.hit();
                createParticle(e.x+15, e.y+15, '#DC143C', 5);
            } else if(checkCol(p, e)) {
                gameState.deathReason = "Slain by Enemy ⚔️";
                gameState.gameOver = true; Sound.death(); showGameOver();
            }
        });
    }

    function triggerLightning(p) {
        gameState.lightning = { active: true, x: p.x+p.width/2, y: p.y+p.height/2, timer: 20 };
        gameState.gameOver = true; gameState.deathReason = "Lightning Strike ⚡";
        document.getElementById('game-over-title').innerText = "STRUCK!";
        document.getElementById('game-over-title').style.color = "#FFD700";
        Sound.lightning();
        createParticle(p.x+20, p.y+20, '#FFFF00', 6);
        setTimeout(showGameOver, 1000);
    }

    function triggerSplash(p) {
        if(gameState.splash.active) return;
        gameState.splash = { active: true, x: p.x+p.width/2, y: p.y+p.height, timer: 30 };
        p.isHumpty = false; 
        gameState.gameOver = true; gameState.deathReason = "Egg Splash 🥚";
        document.getElementById('game-over-title').innerText = "SPLASHED!";
        document.getElementById('game-over-title').style.color = "#00BFFF";
        Sound.splash();
        createParticle(p.x+20, p.y+40, '#F0EAD6', 5);
        setTimeout(showGameOver, 1000);
    }

    function showGameOver() {
        Sound.stopMusic();
        const lb = getLeaderboard();
        let high = false;
        if(lb.length<10 || (lb.length>0 && gameState.score > lb[lb.length-1].score)) high=true;
        
        document.getElementById('game-over-screen').style.display = 'flex';
        document.getElementById('final-stats').innerText = `Level: ${gameState.level} | Score: ${gameState.score}`;
        document.getElementById('high-score-area').style.display = high ? 'flex' : 'none';
        document.getElementById('no-high-score-area').style.display = high ? 'none' : 'flex';
    }

    function updateUI() {
        document.getElementById('score-display').innerText = "Score: " + gameState.score;
        const left = gameState.totalCoins - gameState.coinsCollected;
        let txt = `Level ${gameState.level} • Coins: <span style="color:${left===0?'#32CD32':'#ff5555'}">${left}</span>`;
        if(gameState.player.isHumpty) txt += ` <span style="color:#FFD700">🥚 EGG MODE (${gameState.eggsCollected})</span>`;
        document.getElementById('level-display').innerHTML = txt;
    }

    function draw() {
        // Sky Gradient
        const g = ctx.createLinearGradient(0,0,0,LOGICAL_HEIGHT);
        g.addColorStop(0, '#0B1026'); g.addColorStop(1, '#2B32B2');
        ctx.fillStyle = g; ctx.fillRect(0,0,LOGICAL_WIDTH,LOGICAL_HEIGHT);

        // Stars
        ctx.fillStyle = '#FFF';
        gameState.clouds.forEach(c => {
            if(c.type==='star') { ctx.globalAlpha = Math.random(); ctx.beginPath(); ctx.arc(c.x, c.y, c.s, 0, Math.PI*2); ctx.fill(); }
        });
        ctx.globalAlpha = 1;

        // Mountains (Parallax)
        ctx.fillStyle = '#1A1A2E';
        ctx.beginPath(); ctx.moveTo(0, LOGICAL_HEIGHT);
        for(let i=0; i<=LOGICAL_WIDTH; i+=100) ctx.lineTo(i, LOGICAL_HEIGHT-150-Math.sin(i*0.01 + Date.now()*0.0001)*50);
        ctx.lineTo(LOGICAL_WIDTH, LOGICAL_HEIGHT); ctx.fill();

        // Clouds
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        gameState.clouds.forEach(c => {
            if(c.type==='cloud') {
                ctx.beginPath(); ctx.arc(c.x, c.y, 25*c.scale, 0, Math.PI*2);
                ctx.arc(c.x+20*c.scale, c.y-10*c.scale, 30*c.scale, 0, Math.PI*2);
                ctx.arc(c.x+40*c.scale, c.y, 25*c.scale, 0, Math.PI*2); ctx.fill();
            }
        });
        
        // Wind
        ctx.fillStyle = 'rgba(200, 255, 255, 0.3)';
        gameState.wind.forEach(w => {
            if(w.active) {
                ctx.fillRect(w.x, w.y, w.width, w.height);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
                for(let i=0; i<10; i++) ctx.fillRect(w.x + Math.random()*w.width, w.y + Math.random()*w.height, 2, 40);
                ctx.fillStyle = 'rgba(200, 255, 255, 0.3)';
            }
        });
        
        // Meteors
        gameState.meteors.forEach(m => {
            if(!m.active) return;
            ctx.save();
            ctx.translate(m.x + m.width/2, m.y + m.height/2);
            ctx.rotate(m.rotation);
            ctx.fillStyle = '#FF4500';
            ctx.beginPath();
            ctx.moveTo(-10, -15); ctx.lineTo(10, -10); ctx.lineTo(15, 10); ctx.lineTo(0, 15); ctx.lineTo(-15, 5);
            ctx.fill();
            ctx.restore();
            createParticle(m.x + m.width/2, m.y, '#FFA500', 2);
        });

        // Platforms (Textured)
        gameState.platforms.forEach(p => {
            ctx.fillStyle = '#5D4037'; // Dirt
            ctx.fillRect(p.x, p.y+5, p.width, p.height-5);
            ctx.fillStyle = '#4CAF50'; // Grass Top
            ctx.fillRect(p.x, p.y, p.width, 5);
            // Grass details
            ctx.fillStyle = '#388E3C';
            for(let i=0; i<p.width; i+=10) ctx.fillRect(p.x+i, p.y, 2, 3);
        });

        // Coins
        gameState.coins.forEach(c => {
            if(!c.active) return;
            const cy = c.y + Math.sin(c.float)*5;
            ctx.fillStyle = '#FFD700'; ctx.beginPath(); ctx.arc(c.x+10, cy+10, 8, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = '#FFF'; ctx.beginPath(); ctx.arc(c.x+7, cy+7, 2, 0, Math.PI*2); ctx.fill(); // Shine
        });

        // Enemies
        gameState.enemies.forEach(e => {
            if(!e.active) return;
            const by = e.y - Math.abs(Math.sin(e.bounce)*5);
            ctx.fillStyle = '#DC143C';
            ctx.beginPath(); ctx.arc(e.x+17, by+17, 17, Math.PI, 0); ctx.lineTo(e.x+34, by+34); ctx.lineTo(e.x, by+34); ctx.fill();
            // Angry Eyes
            ctx.fillStyle = '#FFF';
            ctx.fillRect(e.x+8, by+12, 8, 8); ctx.fillRect(e.x+20, by+12, 8, 8);
            ctx.fillStyle = '#000';
            ctx.fillRect(e.x+10, by+14, 4, 4); ctx.fillRect(e.x+22, by+14, 4, 4);
            // Brows
            ctx.beginPath(); ctx.moveTo(e.x+5, by+10); ctx.lineTo(e.x+15, by+15); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(e.x+30, by+10); ctx.lineTo(e.x+20, by+15); ctx.stroke();
        });

        const p = gameState.player;
        if(p.isHumpty) {
            // Static Sparks
            if(gameState.eggsCollected>=3 && p.stationaryTimer>60) {
                const intens = (p.stationaryTimer-60)/120;
                if(Math.random()<intens) {
                    ctx.strokeStyle='#FF0'; ctx.beginPath();
                    ctx.moveTo(p.x+20, p.y+20); ctx.lineTo(p.x+20+(Math.random()-0.5)*40, p.y+20+(Math.random()-0.5)*40); ctx.stroke();
                }
            }
            ctx.save(); ctx.translate(p.x+20, p.y+20); ctx.rotate(p.rotation);
            ctx.fillStyle = '#EEE'; ctx.beginPath(); ctx.ellipse(0,0, 20, 25, 0, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle='#CCC'; ctx.lineWidth=2; ctx.stroke();
            // Face
            ctx.fillStyle='#000'; ctx.beginPath(); ctx.arc(-8,-5,3,0,Math.PI*2); ctx.arc(8,-5,3,0,Math.PI*2); ctx.fill();
            ctx.beginPath(); ctx.arc(0,10,5,0,Math.PI,true); ctx.stroke();
            ctx.restore();
        } else if(!gameState.splash.active) {
            // Ninja Scarf
            if(Math.abs(p.vx)>1) {
                ctx.strokeStyle = '#F00'; ctx.lineWidth = 4;
                ctx.beginPath(); ctx.moveTo(p.x+20, p.y+15);
                ctx.quadraticCurveTo(p.x+(p.facing==='right'?-20:60), p.y+10, p.x+(p.facing==='right'?-40:80), p.y+20+Math.sin(Date.now()*0.02)*10);
                ctx.stroke();
            }
            // Body
            ctx.fillStyle = '#222'; ctx.fillRect(p.x+5, p.y+10, 30, 30);
            ctx.fillStyle = '#FFC107'; ctx.fillRect(p.x+8, p.y, 24, 12); // Skin
            ctx.fillStyle = '#222'; ctx.fillRect(p.x+5, p.y-2, 30, 6); // Headband
            ctx.fillStyle = '#000'; 
            const off = p.facing==='left'?-2:2;
            ctx.fillRect(p.x+14+off, p.y+4, 4, 4); ctx.fillRect(p.x+24+off, p.y+4, 4, 4); // Eyes
            
            if(p.isAttacking) {
                ctx.save(); ctx.translate(p.x+20, p.y+20);
                const prog = (20-p.attackTimer)/20;
                const ang = (-60*Math.PI/180) + ((140*Math.PI/180)*prog);
                if(p.facing==='left') ctx.scale(-1,1);
                ctx.rotate(ang);
                ctx.fillStyle = '#DDD'; ctx.fillRect(10, -4, 40, 8); // Blade
                ctx.fillStyle = '#8B4513'; ctx.fillRect(0, -3, 10, 6); // Handle
                ctx.restore();
                // Swipe FX
                ctx.strokeStyle='rgba(255,255,255,0.5)'; ctx.lineWidth=2;
                ctx.beginPath(); ctx.arc(p.x+20, p.y+20, 45, 0, Math.PI*2); ctx.stroke();
            }
        }

        // Particles
        gameState.particles.forEach(pt => {
            ctx.fillStyle = pt.color; ctx.globalAlpha = pt.life/30;
            ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.size, 0, Math.PI*2); ctx.fill();
        });
        ctx.globalAlpha = 1;

        // FX
        if(gameState.splash.active) {
            ctx.fillStyle = '#FFA500'; // Yolk color
            for(let i=0; i<8; i++) {
                const a = (Math.PI+(Math.PI*(i/8)));
                const d = (30-gameState.splash.timer)*2;
                ctx.beginPath(); ctx.arc(gameState.splash.x+Math.cos(a)*d, gameState.splash.y+Math.sin(a)*d-10, 5, 0, Math.PI*2); ctx.fill();
            }
            if(gameState.splash.timer>0) gameState.splash.timer--;
        }
        if(gameState.lightning.active) {
            const l = gameState.lightning;
            if(l.timer>15) { ctx.fillStyle='rgba(255,255,255,0.8)'; ctx.fillRect(0,0,LOGICAL_WIDTH,LOGICAL_HEIGHT); }
            ctx.strokeStyle='#FF0'; ctx.lineWidth=6; ctx.shadowBlur=15; ctx.shadowColor='#FFF';
            ctx.beginPath(); ctx.moveTo(l.x,0); 
            ctx.lineTo(l.x-15,l.y*0.3); ctx.lineTo(l.x+15,l.y*0.6); ctx.lineTo(l.x,l.y); ctx.stroke();
            ctx.shadowBlur=0;
            if(l.timer>0) l.timer--;
        }
    }

    function gameLoop() { update(); draw(); requestAnimationFrame(gameLoop); }
</script>
</body>
</html>
"""

components.html(game_html, height=650)
