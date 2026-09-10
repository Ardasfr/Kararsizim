/**
 * Kararsızım — High-Performance (60-120 FPS) Decision Wheel Engine
 *
 * Performance Architecture:
 * - Pre-rendered offscreen buffer canvas: All slices, text, gradients and pins are drawn ONCE.
 *   The animation loop only executes a single hardware-accelerated GPU drawImage call.
 * - Zero layout thrashing: No DOM offsetWidth measurements during animation.
 * - 100% Mathematical Precision: The winner is selected first, and the rotation is calculated
 *   to guarantee the arrow lands directly and unambiguously inside the winner's segment.
 * - Web Audio API synthesized mechanical clicks (smoothly throttled, zero lag).
 * - Full Dark & Light Mode theme compliance.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    const stage = document.getElementById('wheel-stage-container');
    if (!stage) return;
    initWheel(stage);
  });

  function initWheel(stage) {
    const canvas = document.getElementById('wheel-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const centerSpinBtn = document.getElementById('center-spin-btn');
    const mainSpinBtn = document.getElementById('main-spin-btn');
    const spinAgainBtn = document.getElementById('spin-again-btn');
    const removeWinnerBtn = document.getElementById('remove-winner-btn');
    const shareResultBtn = document.getElementById('share-result-btn');
    const winnerBanner = document.getElementById('winner-banner');
    const winnerTitle = document.getElementById('winner-title');
    const soundToggleBtn = document.getElementById('sound-toggle-btn');
    const soundIcon = document.getElementById('sound-icon');
    const pointerElem = document.getElementById('wheel-pointer');
    const activeCountBadge = document.getElementById('active-options-count');

    // Parse options from stage data attribute
    const rawOptions = JSON.parse(stage.dataset.options || '[]');
    const wheelId = stage.dataset.wheelId;
    const spinUrl = stage.dataset.spinUrl;

    const PALETTE = [
      '#6C63FF', '#FF6584', '#43C6AC', '#FFB800',
      '#3B82F6', '#EC4899', '#10B981', '#8B5CF6',
      '#F97316', '#06B6D4', '#E11D48', '#84CC16',
      '#6366F1', '#14B8A6', '#F59E0B', '#A855F7'
    ];

    let allOptions = rawOptions.map((opt, i) => ({
      id: opt.id || String(i),
      text: opt.text,
      color: opt.color || PALETTE[i % PALETTE.length],
      enabled: true
    }));

    // Offscreen buffer canvas for 60-120 FPS performance
    const bufferCanvas = document.createElement('canvas');
    const bCtx = bufferCanvas.getContext('2d');

    let currentAngle = 0; // Current rotation in radians
    let isSpinning = false;
    let soundEnabled = true;
    let audioCtx = null;
    let lastTickIdx = -1;
    let lastWinner = null;
    let canvasSize = 520;

    // Audio synthesizer for wooden/mechanical clicks
    function initAudio() {
      if (!audioCtx) {
        const AudioClass = window.AudioContext || window.webkitAudioContext;
        if (AudioClass) audioCtx = new AudioClass();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    }

    let lastSoundTime = 0;
    function playTickSound() {
      if (!soundEnabled || !audioCtx) return;
      const now = audioCtx.currentTime;
      if (now - lastSoundTime < 0.04) return; // Throttle to prevent audio buffer saturation
      lastSoundTime = now;

      try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(520, now);
        osc.frequency.exponentialRampToValueAtTime(140, now + 0.025);

        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.025);

        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.025);
      } catch (e) {}
    }

    function playWinJingle() {
      if (!soundEnabled || !audioCtx) return;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      const baseTime = audioCtx.currentTime;
      notes.forEach((freq, idx) => {
        try {
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          const startTime = baseTime + idx * 0.1;
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, startTime);
          gain.gain.setValueAtTime(0.25, startTime);
          gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.3);
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start(startTime);
          osc.stop(startTime + 0.3);
        } catch (e) {}
      });
    }

    function getActiveOptions() {
      return allOptions.filter(o => o.enabled);
    }

    function updateOptionsCount() {
      const active = getActiveOptions();
      if (activeCountBadge) {
        activeCountBadge.textContent = active.length;
      }
    }

    /**
     * PRE-RENDER WHEEL DISC TO OFFSCREEN BUFFER
     * This executes only on resize or when options change.
     * The spin animation never re-computes text or slice geometries!
     */
    function preRenderWheel() {
      const dpr = window.devicePixelRatio || 1;
      const size = canvasSize * dpr;

      bufferCanvas.width = size;
      bufferCanvas.height = size;

      bCtx.resetTransform && bCtx.resetTransform();
      bCtx.scale(dpr, dpr);

      const centerX = canvasSize / 2;
      const centerY = canvasSize / 2;
      const outerRadius = canvasSize / 2 - 14;
      const innerRadius = Math.max(42, outerRadius * 0.2);

      bCtx.clearRect(0, 0, canvasSize, canvasSize);

      const active = getActiveOptions();
      if (active.length === 0) {
        bCtx.fillStyle = '#9CA3AF';
        bCtx.font = 'bold 16px Nunito, sans-serif';
        bCtx.textAlign = 'center';
        bCtx.textBaseline = 'middle';
        bCtx.fillText('En az 2 seçenek aktif olmalı', centerX, centerY);
        return;
      }

      const arc = (2 * Math.PI) / active.length;

      bCtx.save();
      bCtx.translate(centerX, centerY);

      // 1. Draw Each Segment
      active.forEach((opt, idx) => {
        const startAngle = idx * arc;
        const endAngle = startAngle + arc;

        bCtx.beginPath();
        bCtx.moveTo(0, 0);
        bCtx.arc(0, 0, outerRadius, startAngle, endAngle);
        bCtx.closePath();

        bCtx.fillStyle = opt.color;
        bCtx.fill();

        // Subtle slice separator line
        bCtx.lineWidth = 2;
        bCtx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
        bCtx.stroke();

        // 2. Draw Text along slice radial bisector
        bCtx.save();
        bCtx.rotate(startAngle + arc / 2);
        bCtx.textAlign = 'right';
        bCtx.textBaseline = 'middle';
        bCtx.fillStyle = '#FFFFFF';

        let fontSize = 16;
        if (canvasSize < 340) {
          fontSize = active.length > 10 ? 10 : 12;
        } else if (canvasSize < 420) {
          fontSize = active.length > 12 ? 11 : 13;
        } else if (active.length > 14) {
          fontSize = 12;
        } else if (active.length > 8) {
          fontSize = 14;
        }
        bCtx.font = `800 ${fontSize}px Nunito, -apple-system, sans-serif`;

        // Pre-truncate text to fit slice
        const maxTextWidth = outerRadius - innerRadius - 26;
        let txt = opt.text;
        if (bCtx.measureText(txt).width > maxTextWidth) {
          while (txt.length > 3 && bCtx.measureText(txt + '…').width > maxTextWidth) {
            txt = txt.slice(0, -1);
          }
          txt += '…';
        }

        // Crisp text without expensive runtime shadowBlur
        bCtx.lineWidth = 3;
        bCtx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
        bCtx.strokeText(txt, outerRadius - 18, 0);
        bCtx.fillText(txt, outerRadius - 18, 0);

        bCtx.restore();
      });

      // 3. Outer Rim (Dark sleek border with perimeter dots)
      bCtx.beginPath();
      bCtx.arc(0, 0, outerRadius, 0, 2 * Math.PI);
      bCtx.lineWidth = 8;
      bCtx.strokeStyle = '#181B2A';
      bCtx.stroke();

      // Outer golden/metallic perimeter pins
      active.forEach((_, idx) => {
        const pinAngle = idx * arc;
        const pinX = Math.cos(pinAngle) * (outerRadius - 4);
        const pinY = Math.sin(pinAngle) * (outerRadius - 4);

        bCtx.beginPath();
        bCtx.arc(pinX, pinY, 3.5, 0, 2 * Math.PI);
        bCtx.fillStyle = '#FFD700';
        bCtx.fill();
        bCtx.lineWidth = 1;
        bCtx.strokeStyle = '#181B2A';
        bCtx.stroke();
      });

      // 4. Center Hub base ring
      bCtx.beginPath();
      bCtx.arc(0, 0, innerRadius, 0, 2 * Math.PI);
      bCtx.fillStyle = '#181B2A';
      bCtx.fill();
      bCtx.lineWidth = 4;
      bCtx.strokeStyle = '#272C42';
      bCtx.stroke();

      bCtx.restore();
    }

    // Fast screen rendering: 1 GPU draw call
    function renderFrame() {
      const dpr = window.devicePixelRatio || 1;
      const width = canvasSize;
      const height = canvasSize;
      const centerX = width / 2;
      const centerY = height / 2;

      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(currentAngle);
      ctx.drawImage(bufferCanvas, -centerX, -centerY, width, height);
      ctx.restore();
    }

    // Canvas resize handling
    function resizeCanvas() {
      const container = document.getElementById('wheel-canvas-wrapper');
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const rawWidth = rect.width || container.clientWidth || 480;
      canvasSize = Math.max(240, Math.min(rawWidth, 500));

      const dpr = window.devicePixelRatio || 1;
      canvas.width = canvasSize * dpr;
      canvas.height = canvasSize * dpr;
      canvas.style.width = `${canvasSize}px`;
      canvas.style.height = `${canvasSize}px`;

      ctx.resetTransform && ctx.resetTransform();
      ctx.scale(dpr, dpr);

      preRenderWheel();
      renderFrame();
    }

    window.addEventListener('resize', resizeCanvas);
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => {
        if (!isSpinning) {
          resizeCanvas();
        }
      });
      const container = document.getElementById('wheel-canvas-wrapper');
      if (container) ro.observe(container);
    }

    /**
     * BULLETPROOF SPINNING & NEEDLE ALIGNMENT
     * 1) Randomly select the winning option index.
     * 2) Calculate the exact angle that places this slice directly under the top needle (3*PI/2).
     * 3) Animate with smooth 60fps easing.
     */
    function spinWheel() {
      if (isSpinning) return;
      const active = getActiveOptions();
      if (active.length < 2) {
        alert('Çarkı çevirebilmek için en az 2 aktif seçenek olmalıdır.');
        return;
      }

      initAudio();
      isSpinning = true;
      if (winnerBanner) winnerBanner.style.display = 'none';

      centerSpinBtn.classList.add('is-spinning');
      if (mainSpinBtn) mainSpinBtn.disabled = true;

      // 1. CHOOSE WINNER UPFRONT
      const winningIdx = Math.floor(Math.random() * active.length);
      const winner = active[winningIdx];

      // 2. CALCULATE EXACT TARGET ANGLE
      const arc = (2 * Math.PI) / active.length;
      // Slice center in wheel coords
      const sliceCenter = (winningIdx + 0.5) * arc;

      // Pointer is fixed at top: 3*PI/2 (270 degrees)
      // When wheel rotates by angle A, sliceCenter is at (sliceCenter + A) % 2PI
      // We want: (sliceCenter + targetAngle) % 2PI == 3*PI/2
      // So: targetAngle == 3*PI/2 - sliceCenter (mod 2PI)
      const POINTER_ANGLE = 1.5 * Math.PI; // Top (12 o'clock)
      let baseTargetAngle = POINTER_ANGLE - sliceCenter;

      // Normalize
      while (baseTargetAngle < 0) baseTargetAngle += 2 * Math.PI;

      // Safe jitter inside the slice (stays well away from boundaries)
      const maxJitter = arc * 0.32;
      const jitter = (Math.random() - 0.5) * 2 * maxJitter;

      // Add 6 to 9 full rotations
      const fullRotations = 7 + Math.floor(Math.random() * 3);
      let targetAngle = baseTargetAngle + jitter;

      // Ensure it always spins forward and completes at least 6 turns
      while (targetAngle < currentAngle + fullRotations * 2 * Math.PI) {
        targetAngle += 2 * Math.PI;
      }

      const startAngle = currentAngle;
      const totalDelta = targetAngle - startAngle;
      const duration = 4600 + Math.random() * 500; // ~4.8s
      const startTime = performance.now();

      // Smooth Quintic Easing
      function easeOutQuint(t) {
        return 1 - Math.pow(1 - t, 5);
      }

      function animate(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = easeOutQuint(progress);

        currentAngle = startAngle + totalDelta * eased;

        // Needle tick calculation without layout thrashing
        const currentSliceFloat = ((POINTER_ANGLE - (currentAngle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)) / arc;
        const currentSliceInt = Math.floor(currentSliceFloat);

        if (currentSliceInt !== lastTickIdx) {
          lastTickIdx = currentSliceInt;
          playTickSound();

          if (pointerElem) {
            pointerElem.classList.add('pointer-active');
            setTimeout(() => {
              if (pointerElem) pointerElem.classList.remove('pointer-active');
            }, 50);
          }
        }

        renderFrame();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          // FINISHED
          currentAngle = targetAngle;
          renderFrame();

          isSpinning = false;
          centerSpinBtn.classList.remove('is-spinning');
          if (mainSpinBtn) mainSpinBtn.disabled = false;

          lastWinner = winner;
          onWinnerDetermined(winner);
        }
      }

      requestAnimationFrame(animate);
    }

    function onWinnerDetermined(winner) {
      playWinJingle();
      triggerConfetti();

      if (winnerBanner && winnerTitle) {
        winnerTitle.textContent = winner.text;
        winnerBanner.style.display = 'block';
        winnerBanner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }

      recordSpinInDb();
    }

    function recordSpinInDb() {
      if (!spinUrl) return;
      const match = document.cookie.match(/csrftoken=([^;]+)/);
      const csrf = match ? match[1] : '';

      fetch(spinUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(r => r.json())
      .then(data => {
        if (data.success && data.spin_count !== undefined) {
          const c = document.getElementById('spin-counter-val');
          if (c) c.textContent = data.spin_count;
        }
      })
      .catch(() => {});
    }

    // Lightweight Confetti
    function triggerConfetti() {
      const cCanvas = document.createElement('canvas');
      cCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:99999;';
      document.body.appendChild(cCanvas);

      const cCtx = cCanvas.getContext('2d');
      cCanvas.width = window.innerWidth;
      cCanvas.height = window.innerHeight;

      const particles = [];
      const colors = ['#6C63FF', '#FF6584', '#43C6AC', '#FFB800', '#3B82F6', '#EC4899', '#FFF'];

      for (let i = 0; i < 80; i++) {
        particles.push({
          x: cCanvas.width / 2 + (Math.random() - 0.5) * 140,
          y: cCanvas.height / 2 - 30,
          vx: (Math.random() - 0.5) * 14,
          vy: -Math.random() * 14 - 6,
          size: Math.random() * 8 + 5,
          color: colors[Math.floor(Math.random() * colors.length)],
          rot: Math.random() * 360,
          vRot: (Math.random() - 0.5) * 12,
          gravity: 0.32,
          alpha: 1
        });
      }

      const start = performance.now();
      function renderC(t) {
        const elapsed = t - start;
        cCtx.clearRect(0, 0, cCanvas.width, cCanvas.height);

        particles.forEach(p => {
          p.x += p.vx;
          p.y += p.vy;
          p.vy += p.gravity;
          p.rot += p.vRot;
          p.alpha = Math.max(0, 1 - elapsed / 2400);

          cCtx.save();
          cCtx.translate(p.x, p.y);
          cCtx.rotate((p.rot * Math.PI) / 180);
          cCtx.globalAlpha = p.alpha;
          cCtx.fillStyle = p.color;
          cCtx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.65);
          cCtx.restore();
        });

        if (elapsed < 2400) {
          requestAnimationFrame(renderC);
        } else {
          cCanvas.remove();
        }
      }

      requestAnimationFrame(renderC);
    }

    // Event Listeners
    if (centerSpinBtn) centerSpinBtn.addEventListener('click', spinWheel);
    if (mainSpinBtn) mainSpinBtn.addEventListener('click', spinWheel);
    if (spinAgainBtn) spinAgainBtn.addEventListener('click', spinWheel);

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        spinWheel();
      }
    });

    if (soundToggleBtn) {
      soundToggleBtn.addEventListener('click', () => {
        soundEnabled = !soundEnabled;
        if (soundIcon) soundIcon.textContent = soundEnabled ? '🔊' : '🔇';
        const txt = soundToggleBtn.querySelector('.btn-text');
        if (txt) txt.textContent = soundEnabled ? 'Ses Açık' : 'Ses Kapalı';
      });
    }

    // "Çıkar & Tekrar Çevir"
    if (removeWinnerBtn) {
      removeWinnerBtn.addEventListener('click', () => {
        if (!lastWinner) return;
        const opt = allOptions.find(o => o.id === lastWinner.id);
        if (opt) {
          opt.enabled = false;
          const chip = document.getElementById(`opt-chip-${opt.id}`);
          if (chip) chip.classList.add('is-disabled');
          updateOptionsCount();
          preRenderWheel();
          renderFrame();
          setTimeout(spinWheel, 300);
        }
      });
    }

    // Share result
    if (shareResultBtn) {
      shareResultBtn.addEventListener('click', async () => {
        if (!lastWinner) return;
        const title = document.querySelector('.wheel-detail-title')?.textContent || 'Karar Çarkı';
        const url = window.location.href;
        const text = `🎡 "${title}" çarkı kararını verdi: 👉 ${lastWinner.text}! Sen de çevirip kararını al: ${url}`;

        if (navigator.share) {
          try {
            await navigator.share({ title, text, url });
            return;
          } catch (e) {}
        }

        try {
          await navigator.clipboard.writeText(text);
          shareResultBtn.textContent = '✓ Kopyalandı!';
          setTimeout(() => { shareResultBtn.textContent = '📢 Sonucu Paylaş'; }, 2000);
        } catch (e) {
          prompt('Sonucu kopyalayın:', text);
        }
      });
    }

    // Initial setup
    updateOptionsCount();
    resizeCanvas();
  }
})();
