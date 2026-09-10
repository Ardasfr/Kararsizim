/**
 * Kararsızım — Interactive Frontend Utilities
 * Handles: Theme Toggle, AJAX Voting, Dynamic Choice Inputs, Share Link
 */

function bootMain() {
  initTheme();
  initAccessibility();
  initAjaxVoting();
  initDynamicChoices();
  initShareButtons();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootMain);
} else {
  bootMain();
}

/* ==========================================================================
   1. Theme Management (Dark / Light Mode)
   ========================================================================== */
function initTheme() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  let currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', (e) => {
      // Toggle if not already handled by capture phase
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const nextTheme = (current === 'dark') ? 'light' : 'dark';
      localStorage.setItem('theme', nextTheme);
      applyTheme(nextTheme);
    });
  }

  window.addEventListener('themeChanged', (e) => {
    if (e.detail && e.detail.theme) {
      applyTheme(e.detail.theme);
    }
  });
}

function applyTheme(theme) {
  const doc = document.documentElement;
  doc.setAttribute('data-theme', theme);
  const themeToggleBtn = document.getElementById('theme-toggle');
  const icon = document.getElementById('theme-icon');
  const isDark = theme === 'dark';
  if (icon) {
    icon.textContent = isDark ? '☀️' : '🌙';
  } else if (themeToggleBtn) {
    themeToggleBtn.textContent = isDark ? '☀️' : '🌙';
  }
  if (themeToggleBtn) {
    themeToggleBtn.setAttribute('title', isDark ? 'Aydınlık moda geç' : 'Karanlık moda geç');
    themeToggleBtn.setAttribute('aria-label', isDark ? 'Aydınlık moda geç' : 'Karanlık moda geç');
  }
}

/* ==========================================================================
   2. AJAX Voting with Smooth Transition
   ========================================================================== */
function initAjaxVoting() {
  const voteForms = document.querySelectorAll('.poll-choices-form');

  voteForms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const submitter = e.submitter || document.activeElement;
      const choicesList = form.querySelector('.choices-list');

      // Instant UI Feedback (0ms delay)
      if (submitter && submitter.classList.contains('choice-btn')) {
        submitter.classList.add('is-submitting');
        const arrow = submitter.querySelector('.choice-arrow');
        if (arrow) arrow.textContent = '⏳';
      }
      if (choicesList) {
        choicesList.classList.add('is-voting');
      }

      let formData;
      try {
        formData = new FormData(form, submitter);
      } catch (err) {
        formData = new FormData(form);
      }

      if (submitter && submitter.name === 'choice') {
        formData.set('choice', submitter.value);
      }
      formData.append('ajax', '1');

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (response.ok && data.success) {
          renderPollResults(form.closest('.poll-card'), data);
          showToast(data.message || 'Oyunuz kaydedildi! 🎉');
        } else {
          if (submitter) submitter.classList.remove('is-submitting');
          if (choicesList) choicesList.classList.remove('is-voting');
          const arrow = submitter ? submitter.querySelector('.choice-arrow') : null;
          if (arrow) arrow.textContent = '→';

          showToast(data.error || 'Bir hata oluştu.', 'error');
          if (data.already_voted) {
            setTimeout(() => window.location.reload(), 1200);
          }
        }
      } catch (err) {
        console.error('Oy gönderme hatası:', err);
        // Fallback to standard submit
        form.submit();
      }
    });
  });
}

function renderPollResults(cardElement, data) {
  if (!cardElement) return;

  const choicesContainer = cardElement.querySelector('.poll-body');
  if (!choicesContainer) return;

  let resultsHtml = `<div class="poll-results-list" role="region" aria-label="Anket Sonuçları" aria-live="polite">`;

  data.choices.forEach(c => {
    const isSelected = c.is_selected;
    resultsHtml += `
      <div class="result-item ${isSelected ? 'user-selected' : ''}">
        <div class="result-item-bar" style="width: 0%" data-target-width="${c.percentage}%"></div>
        <div class="result-text">
          <span>${escapeHtml(c.text)}</span>
          ${isSelected ? '<span class="result-badge">Senin Oyun</span>' : ''}
        </div>
        <div class="result-stats">
          <span class="result-percentage">${c.percentage}%</span>
          <span class="result-count">(${c.votes} oy)</span>
        </div>
      </div>
    `;
  });

  resultsHtml += `</div>`;
  choicesContainer.innerHTML = resultsHtml;

  // Update footer total votes
  const totalVotesCount = cardElement.querySelector('.total-votes-count');
  if (totalVotesCount) {
    totalVotesCount.textContent = data.total_votes;
  }

  // Animate progress bars
  requestAnimationFrame(() => {
    cardElement.querySelectorAll('.result-item-bar').forEach(bar => {
      const targetWidth = bar.getAttribute('data-target-width');
      bar.style.width = targetWidth;
    });
  });
}

/* ==========================================================================
   3. Dynamic Choice Inputs for Poll Creation
   ========================================================================== */
function initDynamicChoices() {
  const choicesContainer = document.getElementById('dynamic-choices-container');
  const addChoiceBtn = document.getElementById('add-choice-btn');

  if (!choicesContainer || !addChoiceBtn) return;

  const MAX_CHOICES = 5;
  const MIN_CHOICES = 2;

  function updateButtonsState() {
    const rows = choicesContainer.querySelectorAll('.choice-row');
    addChoiceBtn.disabled = rows.length >= MAX_CHOICES;
    if (rows.length >= MAX_CHOICES) {
      addChoiceBtn.style.opacity = '0.5';
      addChoiceBtn.style.cursor = 'not-allowed';
    } else {
      addChoiceBtn.style.opacity = '1';
      addChoiceBtn.style.cursor = 'pointer';
    }

    rows.forEach(row => {
      const removeBtn = row.querySelector('.choice-remove-btn');
      if (removeBtn) {
        removeBtn.style.display = rows.length > MIN_CHOICES ? 'flex' : 'none';
      }
    });
  }

  addChoiceBtn.addEventListener('click', () => {
    const currentRows = choicesContainer.querySelectorAll('.choice-row');
    if (currentRows.length >= MAX_CHOICES) return;

    const nextIndex = currentRows.length + 1;
    const newRow = document.createElement('div');
    newRow.className = 'choice-row';
    newRow.innerHTML = `
      <input type="text" name="choices[]" class="form-input" placeholder="${nextIndex}. Seçenek" maxlength="100" required autocomplete="off">
      <button type="button" class="choice-remove-btn" title="Seçeneği kaldır">&times;</button>
    `;

    choicesContainer.appendChild(newRow);
    newRow.querySelector('input').focus();
    updateButtonsState();
  });

  choicesContainer.addEventListener('click', (e) => {
    if (e.target.closest('.choice-remove-btn')) {
      const currentRows = choicesContainer.querySelectorAll('.choice-row');
      if (currentRows.length > MIN_CHOICES) {
        const row = e.target.closest('.choice-row');
        row.remove();
        updateButtonsState();
      }
    }
  });

  updateButtonsState();
}

/* ==========================================================================
   4. Share Button (Native Web Share API with Clipboard Fallback)
   ========================================================================== */
function initShareButtons() {
  document.addEventListener('click', async (e) => {
    const shareBtn = e.target.closest('.btn-share');
    if (!shareBtn) return;

    const url = shareBtn.getAttribute('data-url') || window.location.href;
    const title = shareBtn.getAttribute('data-title') || '🤔 Kararsızım — Bir oy da sen ver!';

    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: '🤔 Kararsızım! Bu ankette senin fikrin ne? Bir oy da sen ver:',
          url: url
        });
        return;
      } catch (err) {
        if (err.name === 'AbortError') {
          return; // Kullanıcı paylaşımı iptal etti
        }
      }
    }

    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(url);
        showToast('🔗 Bağlantı panoya kopyalandı! Arkadaşlarınla paylaşabilirsin.');
      } else {
        showToast('Bağlantı: ' + url);
      }
    } catch (err) {
      showToast('Kopyalama başarısız oldu.', 'error');
    }
  });
}

/* ==========================================================================
   5. Accessibility (A11y) Manager
   ========================================================================== */
function initAccessibility() {
  const a11yToggleBtn = document.getElementById('a11y-toggle');
  const a11yModal = document.getElementById('a11y-modal');
  const a11yCloseBtn = document.getElementById('a11y-modal-close');
  const a11ySaveCloseBtn = document.getElementById('a11y-save-close-btn');
  const a11yResetBtn = document.getElementById('a11y-reset-btn');

  const sizeBtns = document.querySelectorAll('.a11y-size-btn');
  const contrastToggle = document.getElementById('a11y-contrast-toggle');
  const fontToggle = document.getElementById('a11y-font-toggle');
  const motionToggle = document.getElementById('a11y-motion-toggle');
  const underlineToggle = document.getElementById('a11y-underline-toggle');

  const STORAGE_KEY = 'kararsizim_a11y_settings';
  const defaultSettings = {
    fontSize: 'normal',
    highContrast: false,
    dyslexicFont: false,
    reduceMotion: false,
    underlineLinks: false
  };

  let currentSettings = loadSettings();
  applySettings(currentSettings);

  function loadSettings() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? { ...defaultSettings, ...JSON.parse(saved) } : { ...defaultSettings };
    } catch (e) {
      return { ...defaultSettings };
    }
  }

  function saveSettings(settings) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch (e) {}
  }

  function applySettings(s) {
    const html = document.documentElement;

    // Font size
    if (s.fontSize === 'normal') {
      html.removeAttribute('data-a11y-font-size');
    } else {
      html.setAttribute('data-a11y-font-size', s.fontSize);
    }
    sizeBtns.forEach(btn => {
      const match = btn.getAttribute('data-size') === s.fontSize;
      btn.setAttribute('aria-pressed', match ? 'true' : 'false');
    });

    // High Contrast
    if (s.highContrast) {
      html.setAttribute('data-a11y-contrast', 'high');
      if (contrastToggle) contrastToggle.setAttribute('aria-checked', 'true');
    } else {
      html.removeAttribute('data-a11y-contrast');
      if (contrastToggle) contrastToggle.setAttribute('aria-checked', 'false');
    }

    // Dyslexic font
    if (s.dyslexicFont) {
      html.setAttribute('data-a11y-font', 'dyslexic');
      if (fontToggle) fontToggle.setAttribute('aria-checked', 'true');
    } else {
      html.removeAttribute('data-a11y-font');
      if (fontToggle) fontToggle.setAttribute('aria-checked', 'false');
    }

    // Reduce Motion
    if (s.reduceMotion) {
      html.setAttribute('data-a11y-motion', 'reduced');
      if (motionToggle) motionToggle.setAttribute('aria-checked', 'true');
    } else {
      html.removeAttribute('data-a11y-motion');
      if (motionToggle) motionToggle.setAttribute('aria-checked', 'false');
    }

    // Underline links
    if (s.underlineLinks) {
      html.setAttribute('data-a11y-underline', 'true');
      if (underlineToggle) underlineToggle.setAttribute('aria-checked', 'true');
    } else {
      html.removeAttribute('data-a11y-underline');
      if (underlineToggle) underlineToggle.setAttribute('aria-checked', 'false');
    }
  }

  function openModal() {
    if (!a11yModal) return;
    a11yModal.classList.add('is-active');
    a11yModal.setAttribute('aria-hidden', 'false');
    if (a11yToggleBtn) a11yToggleBtn.setAttribute('aria-expanded', 'true');
    if (a11yCloseBtn) a11yCloseBtn.focus();
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!a11yModal) return;
    a11yModal.classList.remove('is-active');
    a11yModal.setAttribute('aria-hidden', 'true');
    if (a11yToggleBtn) {
      a11yToggleBtn.setAttribute('aria-expanded', 'false');
      a11yToggleBtn.focus();
    }
    document.body.style.overflow = '';
  }

  document.querySelectorAll('.a11y-trigger-btn').forEach(btn => {
    btn.addEventListener('click', openModal);
  });
  if (a11yCloseBtn) {
    a11yCloseBtn.addEventListener('click', closeModal);
  }
  if (a11ySaveCloseBtn) {
    a11ySaveCloseBtn.addEventListener('click', closeModal);
  }

  if (a11yModal) {
    a11yModal.addEventListener('click', (e) => {
      if (e.target === a11yModal) {
        closeModal();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && a11yModal && a11yModal.classList.contains('is-active')) {
      closeModal();
    }
  });

  sizeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      currentSettings.fontSize = btn.getAttribute('data-size');
      applySettings(currentSettings);
      saveSettings(currentSettings);
    });
  });

  if (contrastToggle) {
    contrastToggle.addEventListener('click', () => {
      currentSettings.highContrast = !currentSettings.highContrast;
      applySettings(currentSettings);
      saveSettings(currentSettings);
    });
  }

  if (fontToggle) {
    fontToggle.addEventListener('click', () => {
      currentSettings.dyslexicFont = !currentSettings.dyslexicFont;
      applySettings(currentSettings);
      saveSettings(currentSettings);
    });
  }

  if (motionToggle) {
    motionToggle.addEventListener('click', () => {
      currentSettings.reduceMotion = !currentSettings.reduceMotion;
      applySettings(currentSettings);
      saveSettings(currentSettings);
    });
  }

  if (underlineToggle) {
    underlineToggle.addEventListener('click', () => {
      currentSettings.underlineLinks = !currentSettings.underlineLinks;
      applySettings(currentSettings);
      saveSettings(currentSettings);
    });
  }

  if (a11yResetBtn) {
    a11yResetBtn.addEventListener('click', () => {
      currentSettings = { ...defaultSettings };
      applySettings(currentSettings);
      saveSettings(currentSettings);
      showToast('Erişilebilirlik ayarları varsayılana sıfırlandı.');
    });
  }
}

/* ==========================================================================
   6. Helper Utilities
   ========================================================================== */
function showToast(message, type = 'success') {
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.innerHTML = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

