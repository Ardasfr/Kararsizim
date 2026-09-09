/**
 * Kararsızım — Interactive Frontend Utilities
 * Handles: Theme Toggle, AJAX Voting, Dynamic Choice Inputs, Share Link
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAjaxVoting();
  initDynamicChoices();
  initShareButtons();
});

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
    themeToggleBtn.addEventListener('click', () => {
      currentTheme = (currentTheme === 'dark') ? 'light' : 'dark';
      localStorage.setItem('theme', currentTheme);
      applyTheme(currentTheme);
    });
  }
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const themeToggleBtn = document.getElementById('theme-toggle');
  if (themeToggleBtn) {
    themeToggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
    themeToggleBtn.setAttribute('title', theme === 'dark' ? 'Aydınlık moda geç' : 'Karanlık moda geç');
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

  let resultsHtml = `<div class="poll-results-list">`;

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
   4. Share Button (Clipboard copy)
   ========================================================================== */
function initShareButtons() {
  document.addEventListener('click', async (e) => {
    const shareBtn = e.target.closest('.btn-share');
    if (!shareBtn) return;

    const url = shareBtn.getAttribute('data-url') || window.location.href;
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(url);
        showToast('🔗 Bağlantı panoya kopyalandı!');
      } else {
        showToast('Bağlantı: ' + url);
      }
    } catch (err) {
      showToast('Kopyalama başarısız oldu.', 'error');
    }
  });
}

/* ==========================================================================
   5. Helper Utilities
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
