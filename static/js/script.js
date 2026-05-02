document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('email-text');
    const charCount = document.getElementById('char-count');
    const analyzeBtn = document.getElementById('analyze-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');
    const emptyState = document.getElementById('empty-state');
    const resultsContent = document.getElementById('results-content');
    const verdictBadge = document.getElementById('verdict-badge');
    const gaugeFill = document.getElementById('gauge-fill');
    const gaugeLabel = document.getElementById('gauge-label');
    const probSpam = document.getElementById('prob-spam');
    const probHam = document.getElementById('prob-ham');
    const spamPct = document.getElementById('spam-pct');
    const hamPct = document.getElementById('ham-pct');
    const keywordsChips = document.getElementById('keywords-chips');
    const keywordsSection = document.getElementById('keywords-section');

    const SPAM_WORDS = ['free','win','winner','prize','click','urgent','offer','credit','cash','guarantee','unsubscribe','congratulations','claim','limited','act now','buy','discount','earn','million','money','order','profit','deal','lowest','save','bonus','gift','subscribe','trial','investment'];

    // Character count
    textarea.addEventListener('input', () => {
        charCount.textContent = `${textarea.value.length} characters`;
    });

    // Navbar scroll
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    });

    // CountUp on scroll
    const statCards = document.querySelectorAll('.stat-card');
    let statsCounted = false;
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !statsCounted) {
                statsCounted = true;
                statCards.forEach(card => {
                    const target = parseFloat(card.dataset.target);
                    const suffix = card.dataset.suffix || '';
                    const prefix = card.dataset.prefix || '';
                    const numEl = card.querySelector('.stat-number');
                    const isDecimal = target % 1 !== 0;
                    const duration = 1800;
                    const start = performance.now();
                    const animate = (now) => {
                        const elapsed = now - start;
                        const progress = Math.min(elapsed / duration, 1);
                        const eased = 1 - Math.pow(1 - progress, 3);
                        const current = isDecimal ? (eased * target).toFixed(1) : Math.floor(eased * target).toLocaleString();
                        numEl.textContent = `${prefix}${current}${suffix}`;
                        if (progress < 1) requestAnimationFrame(animate);
                    };
                    requestAnimationFrame(animate);
                });
            }
        });
    }, { threshold: 0.3 });
    const statsBar = document.getElementById('stats-bar');
    if (statsBar) statsObserver.observe(statsBar);

    // Card tilt
    statCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `translateY(-4px) perspective(600px) rotateY(${x * 6}deg) rotateX(${-y * 6}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // Analyze
    analyzeBtn.addEventListener('click', async () => {
        const text = textarea.value.trim();
        if (!text) { alert('Please paste some email content first!'); return; }

        analyzeBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        emptyState.classList.add('hidden');
        resultsContent.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
            const data = await response.json();

            if (data.status === 'success') {
                showResults(data.label, data.confidence, text);
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        } catch (err) {
            alert('Connection error: ' + err.message);
        } finally {
            analyzeBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
        }
    });

    function showResults(label, confidence, originalText) {
        resultsContent.classList.remove('hidden');
        emptyState.classList.add('hidden');

        const isSpam = label.toLowerCase() === 'spam';

        // Verdict
        verdictBadge.textContent = isSpam ? 'SPAM' : 'HAM ✓';
        verdictBadge.className = 'verdict-badge ' + (isSpam ? 'verdict-spam' : 'verdict-ham');
        // Re-trigger animation
        verdictBadge.style.animation = 'none';
        verdictBadge.offsetHeight; // reflow
        verdictBadge.style.animation = '';

        // Gauge
        const circumference = 236;
        const offset = circumference - (confidence / 100) * circumference;
        gaugeFill.style.stroke = isSpam ? 'var(--spam-red)' : 'var(--ham-green)';
        gaugeFill.style.strokeDashoffset = circumference; // reset
        setTimeout(() => { gaugeFill.style.strokeDashoffset = offset; }, 50);
        gaugeLabel.textContent = confidence + '%';
        gaugeLabel.style.color = isSpam ? 'var(--spam-red)' : 'var(--ham-green)';

        // Probability bar
        const spamP = isSpam ? confidence : (100 - confidence);
        const hamP = 100 - spamP;
        probSpam.style.width = '0%';
        probHam.style.width = '0%';
        setTimeout(() => {
            probSpam.style.width = spamP + '%';
            probHam.style.width = hamP + '%';
        }, 100);
        spamPct.textContent = spamP.toFixed(1) + '% Spam';
        hamPct.textContent = hamP.toFixed(1) + '% Ham';

        // Keywords
        keywordsChips.innerHTML = '';
        const textLower = originalText.toLowerCase();
        const found = SPAM_WORDS.filter(w => textLower.includes(w));
        if (found.length > 0) {
            keywordsSection.style.display = '';
            found.forEach((word, i) => {
                const chip = document.createElement('span');
                chip.className = 'keyword-chip';
                chip.textContent = word;
                chip.style.animationDelay = (i * 0.08) + 's';
                keywordsChips.appendChild(chip);
            });
        } else {
            keywordsSection.style.display = 'none';
        }

        // Add to recent table
        addToRecent(originalText, label, confidence);

        // Scroll to results
        document.getElementById('result-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function addToRecent(text, label, confidence) {
        const tbody = document.getElementById('recent-body');
        const preview = text.length > 50 ? text.substring(0, 50) + '...' : text;
        const isSpam = label.toLowerCase() === 'spam';
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="preview-cell">${escapeHtml(preview)}</td>
            <td><span class="chip ${isSpam ? 'chip-spam' : 'chip-ham'}">${label.toUpperCase()}</span></td>
            <td class="mono">${confidence}%</td>
            <td class="mono">just now</td>
        `;
        tbody.insertBefore(row, tbody.firstChild);
        if (tbody.children.length > 8) tbody.removeChild(tbody.lastChild);
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
});
