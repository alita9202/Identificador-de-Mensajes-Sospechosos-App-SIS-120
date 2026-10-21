/**
 * SMS SHIELD SIS120 - JAVASCRIPT PRINCIPAL
 * Integración frontend con el motor Flask y re de Python
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // ESTADO DE LA APLICACIÓN
    // -------------------------------------------------------------------------
    let currentPatterns = [];
    let inboxMessages = [];
    let simulatedPool = [];
    let poolIndex = 0;
    let selectedMessageForModal = null;

    // -------------------------------------------------------------------------
    // ELEMENTOS DEL DOM
    // -------------------------------------------------------------------------
    // Navegación
    const navTabs = document.querySelectorAll('.nav-tab');
    const screenViews = document.querySelectorAll('.screen-view');
    const statusClock = document.getElementById('statusClock');
    const inboxUnreadDot = document.getElementById('inboxUnreadDot');

    // Bandeja de Entrada
    const inboxMessagesList = document.getElementById('inboxMessagesList');
    const btnSimulateArrival = document.getElementById('btnSimulateArrival');

    // Analizador
    const customMessageInput = document.getElementById('customMessageInput');
    const charCounter = document.getElementById('charCounter');
    const btnClearInput = document.getElementById('btnClearInput');
    const btnRunAnalysis = document.getElementById('btnRunAnalysis');
    const analysisSpinner = document.getElementById('analysisSpinner');
    const analysisIcon = document.getElementById('analysisIcon');
    const analysisBtnText = document.getElementById('analysisBtnText');
    const presetChips = document.querySelectorAll('.chip-btn');

    // Resultados de Análisis
    const analysisResultsContainer = document.getElementById('analysisResultsContainer');
    const classificationCard = document.getElementById('classificationCard');
    const classificationIcon = document.getElementById('classificationIcon');
    const classificationBadge = document.getElementById('classificationBadge');
    const classificationTitle = document.getElementById('classificationTitle');
    const statCategoriesCount = document.getElementById('statCategoriesCount');
    const statTotalMatches = document.getElementById('statTotalMatches');
    const recommendationText = document.getElementById('recommendationText');
    const academicNote = document.getElementById('academicNote');
    const highlightedTextBox = document.getElementById('highlightedTextBox');
    const detectedMatchesList = document.getElementById('detectedMatchesList');

    // Laboratorio Regex
    const patternSelect = document.getElementById('patternSelect');
    const labPatternCategory = document.getElementById('labPatternCategory');
    const labPatternName = document.getElementById('labPatternName');
    const labPatternRegex = document.getElementById('labPatternRegex');
    const btnCopyRegex = document.getElementById('btnCopyRegex');
    const labPatternFlags = document.getElementById('labPatternFlags');
    const labPatternExplanation = document.getElementById('labPatternExplanation');
    const labOperatorsTable = document.getElementById('labOperatorsTable');
    const btnSampleMatch = document.getElementById('btnSampleMatch');
    const btnSampleNoMatch = document.getElementById('btnSampleNoMatch');
    const labTestInput = document.getElementById('labTestInput');
    const btnRunLabTest = document.getElementById('btnRunLabTest');
    const labResultBox = document.getElementById('labResultBox');
    const labResultStatus = document.getElementById('labResultStatus');
    const labResultContent = document.getElementById('labResultContent');

    // Historial
    const historyList = document.getElementById('historyList');
    const btnClearHistory = document.getElementById('btnClearHistory');

    // Modales y Controles Externos
    const smartphoneFrame = document.getElementById('smartphoneFrame');
    const toggleFrameBtn = document.getElementById('toggleFrameBtn');
    const frameToggleText = document.getElementById('frameToggleText');
    const quickHelpBtn = document.getElementById('quickHelpBtn');
    const guideModal = document.getElementById('guideModal');
    const guideCloseBtn = document.getElementById('guideCloseBtn');
    const guideOkBtn = document.getElementById('guideOkBtn');

    const messageModal = document.getElementById('messageModal');
    const modalSenderAvatar = document.getElementById('modalSenderAvatar');
    const modalSenderName = document.getElementById('modalSenderName');
    const modalTime = document.getElementById('modalTime');
    const modalMessageText = document.getElementById('modalMessageText');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');
    const modalAnalyzeBtn = document.getElementById('modalAnalyzeBtn');

    const toastContainer = document.getElementById('toastContainer');

    // -------------------------------------------------------------------------
    // RELOJ DIGITAL DE LA BARRA DE ESTADO
    // -------------------------------------------------------------------------
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        if (statusClock) {
            statusClock.textContent = `${hours}:${minutes}`;
        }
    }
    updateClock();
    setInterval(updateClock, 30000);

    // -------------------------------------------------------------------------
    // CAMBIO DE PANTALLAS (TAB NAVIGATION)
    // -------------------------------------------------------------------------
    function switchTab(targetViewId) {
        navTabs.forEach(tab => {
            const isMatch = tab.getAttribute('data-target') === targetViewId;
            tab.classList.toggle('active', isMatch);
        });

        screenViews.forEach(view => {
            const isMatch = view.id === targetViewId;
            view.classList.toggle('active', isMatch);
        });

        if (targetViewId === 'viewInbox' && inboxUnreadDot) {
            inboxUnreadDot.style.display = 'none';
        }

        if (targetViewId === 'viewHistory') {
            renderHistory();
        }
    }

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-target');
            if (target) switchTab(target);
        });
    });

    // -------------------------------------------------------------------------
    // UTILIDADES: TOAST NOTIFICATIONS Y ESCAPE HTML SEGURO
    // -------------------------------------------------------------------------
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        if (type === 'warning') icon = '⚠️';

        toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // -------------------------------------------------------------------------
    // CARGAR DATOS INICIALES DESDE FLASK
    // -------------------------------------------------------------------------
    async function loadInitialData() {
        try {
            // Cargar mensajes ficticios
            const resMsgs = await fetch('/api/mock-messages');
            const dataMsgs = await resMsgs.json();
            inboxMessages = dataMsgs.initial || [];
            simulatedPool = dataMsgs.simulated_pool || [];
            renderInbox();

            // Cargar patrones regex
            const resPat = await fetch('/api/patterns');
            currentPatterns = await resPat.json();
            setupLabPatterns();
        } catch (error) {
            console.error('Error cargando datos iniciales:', error);
            showToast('Error al conectar con el servidor Flask', 'warning');
        }
    }

    // -------------------------------------------------------------------------
    // BANDEJA DE ENTRADA SIMULADA
    // -------------------------------------------------------------------------
    function renderInbox() {
        if (!inboxMessagesList) return;
        inboxMessagesList.innerHTML = '';

        inboxMessages.forEach(msg => {
            const card = document.createElement('div');
            card.className = 'message-card';
            card.setAttribute('data-id', msg.id);

            let typeBadgeLabel = 'Normal';
            let badgeClass = 'badge-type-normal';

            if (msg.type_hint === 'urgencia') {
                typeBadgeLabel = 'Urgencia';
                badgeClass = 'badge-type-urgencia';
            } else if (msg.type_hint === 'dinero') {
                typeBadgeLabel = 'Monto Bs';
                badgeClass = 'badge-type-dinero';
            } else if (msg.type_hint === 'datos') {
                typeBadgeLabel = 'Datos';
                badgeClass = 'badge-type-datos';
            } else if (msg.type_hint === 'enlace') {
                typeBadgeLabel = 'Enlace';
                badgeClass = 'badge-type-enlace';
            } else if (msg.type_hint === 'sospechoso') {
                typeBadgeLabel = 'Sospechoso';
                badgeClass = 'badge-type-sospechoso';
            }

            card.innerHTML = `
                <div class="avatar-circle">${escapeHtml(msg.avatar)}</div>
                <div class="message-content-wrapper">
                    <div class="message-top-row">
                        <span class="message-sender">${escapeHtml(msg.sender)}</span>
                        <span class="message-time">${escapeHtml(msg.time)}</span>
                    </div>
                    <p class="message-preview">${escapeHtml(msg.text)}</p>
                    <span class="message-type-badge ${badgeClass}">${typeBadgeLabel}</span>
                </div>
            `;

            card.addEventListener('click', () => openMessageModal(msg));
            inboxMessagesList.appendChild(card);
        });
    }

    function openMessageModal(msg) {
        selectedMessageForModal = msg;
        modalSenderAvatar.textContent = msg.avatar;
        modalSenderName.textContent = msg.sender;
        modalTime.textContent = msg.time;
        modalMessageText.textContent = msg.text;
        messageModal.style.display = 'flex';
    }

    function closeMessageModal() {
        messageModal.style.display = 'none';
        selectedMessageForModal = null;
    }

    modalCloseBtn?.addEventListener('click', closeMessageModal);
    modalCancelBtn?.addEventListener('click', closeMessageModal);
    messageModal?.addEventListener('click', (e) => {
        if (e.target === messageModal) closeMessageModal();
    });

    modalAnalyzeBtn?.addEventListener('click', () => {
        if (!selectedMessageForModal) return;
        const textToAnalyze = selectedMessageForModal.text;
        closeMessageModal();
        customMessageInput.value = textToAnalyze;
        updateCharCounter();
        switchTab('viewAnalyze');
        executeAnalysis(textToAnalyze);
    });

    // Botón Simular Llegada
    btnSimulateArrival?.addEventListener('click', () => {
        if (!simulatedPool.length) return;
        const sample = simulatedPool[poolIndex % simulatedPool.length];
        poolIndex++;

        const now = new Date();
        const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

        const newMsg = {
            id: 'msg-' + Date.now(),
            sender: sample.sender,
            avatar: sample.avatar,
            time: timeStr,
            text: sample.text,
            type_hint: sample.type_hint
        };

        inboxMessages.unshift(newMsg);
        renderInbox();

        // Agregar animación a la primera tarjeta
        const firstCard = inboxMessagesList.querySelector('.message-card');
        if (firstCard) {
            firstCard.classList.add('new-arrival');
        }

        // Si no estamos en la pestaña de bandeja, encender punto de notificación
        const currentActive = document.querySelector('.screen-view.active');
        if (currentActive && currentActive.id !== 'viewInbox') {
            inboxUnreadDot.style.display = 'block';
        }

        showToast(`Nuevo mensaje recibido de "${newMsg.sender}"`, 'success');
    });

    // -------------------------------------------------------------------------
    // ANALIZADOR DE MENSAJES
    // -------------------------------------------------------------------------
    function updateCharCounter() {
        const length = customMessageInput.value.length;
        charCounter.textContent = `${length} / 2000 caracteres`;
    }

    customMessageInput?.addEventListener('input', updateCharCounter);

    btnClearInput?.addEventListener('click', () => {
        customMessageInput.value = '';
        updateCharCounter();
        analysisResultsContainer.style.display = 'none';
    });

    // Casos de prueba preconfigurados para demostración rápida
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const presetId = chip.getAttribute('data-preset');
            let sampleText = '';

            switch (presetId) {
                case '1':
                    sampleText = 'URGENTE: ganaste Bs 5000. Verifica tus datos hoy!!';
                    break;
                case '2':
                    sampleText = 'Su tarjeta de crédito ha sido cancelada, contáctese a este número 77747902 para reactivarla y siga los pasos';
                    break;
                case '3':
                    sampleText = 'Tu cuenta será bloqueada; verifica tus datos inmediatamente';
                    break;
                case '4':
                    sampleText = 'Mi tarjeta de crédito está cancelada desde hace meses y ya fui al banco';
                    break;
                case '5':
                    sampleText = 'Mañana tengo una reunión normal en la universidad';
                    break;
                case '6':
                    sampleText = 'Aviso: su cuenta bancaria cerrada por actividad inusual. Envíe su número de tarjeta, fecha de vencimiento y número de seguro social a soporte@banco-alerta.com';
                    break;
            }

            customMessageInput.value = sampleText;
            updateCharCounter();
            executeAnalysis(sampleText);
        });
    });

    btnRunAnalysis?.addEventListener('click', () => {
        const text = customMessageInput.value.trim();
        if (!text) {
            showToast('Por favor escribe o pega un mensaje para analizar', 'warning');
            customMessageInput.focus();
            return;
        }
        executeAnalysis(text);
    });

    async function executeAnalysis(text) {
        if (!text || !text.trim()) return;

        // Estado de carga visual
        setAnalysisLoading(true);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Error al comunicarse con Python');
            }

            const result = await response.json();
            renderAnalysisResults(result);
            saveToHistory(result);
        } catch (error) {
            console.error('Error en análisis:', error);
            showToast(error.message, 'warning');
        } finally {
            setAnalysisLoading(false);
        }
    }

    function setAnalysisLoading(isLoading) {
        btnRunAnalysis.disabled = isLoading;
        if (isLoading) {
            analysisSpinner.style.display = 'inline-block';
            analysisIcon.style.display = 'none';
            analysisBtnText.textContent = 'Evaluando con Python re...';
        } else {
            analysisSpinner.style.display = 'none';
            analysisIcon.style.display = 'inline-block';
            analysisBtnText.textContent = 'Analizar mensaje con Python';
        }
    }

    // -------------------------------------------------------------------------
    // RENDERIZADO DE RESULTADOS DEL ANÁLISIS
    // -------------------------------------------------------------------------
    function renderAnalysisResults(result) {
        analysisResultsContainer.style.display = 'flex';

        const cls = result.classification;

        // 1. Tarjeta de clasificación orientativa
        classificationCard.className = `classification-card ${cls.badge_class}`;
        classificationTitle.textContent = cls.title;
        recommendationText.textContent = cls.recommendation;
        academicNote.textContent = cls.academic_disclaimer;

        statCategoriesCount.textContent = result.categories_count;
        statTotalMatches.textContent = result.total_matches;

        if (cls.severity === 'safe') {
            classificationIcon.textContent = '🛡️';
            classificationBadge.textContent = 'REGLA: 0 CATEGORÍAS';
        } else if (cls.severity === 'warning') {
            classificationIcon.textContent = '⚠️';
            classificationBadge.textContent = 'REGLA: 1 CATEGORÍA';
        } else {
            classificationIcon.textContent = '🚨';
            classificationBadge.textContent = `REGLA: ${result.categories_count} CATEGORÍAS DISTINTAS`;
        }

        // 2. Resaltado Seguro de Texto (Evita XSS)
        renderSafeHighlightedText(result.text, result.matches);

        // 3. Lista detallada de coincidencias exactas en Python
        renderDetectedMatchesList(result.matches);

        // Scroll suave hacia los resultados
        setTimeout(() => {
            classificationCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    /**
     * Construcción de resaltado seguro en HTML:
     * - Divide el texto por los rangos [start, end] devueltos por re.finditer() de Python.
     * - Escapa rigurosamente todos los fragmentos antes de insertarlos como HTML.
     */
    function renderSafeHighlightedText(originalText, matches) {
        if (!matches || matches.length === 0) {
            highlightedTextBox.innerHTML = `<em>${escapeHtml(originalText)}</em>`;
            return;
        }

        // Ordenamos las coincidencias por posición de inicio (ascendente)
        const sorted = [...matches].sort((a, b) => a.start - b.start);

        let htmlOutput = '';
        let lastIndex = 0;

        for (const m of sorted) {
            // Evitar solapamientos si existieran
            if (m.start < lastIndex) continue;

            // Fragmento de texto normal anterior
            if (m.start > lastIndex) {
                htmlOutput += escapeHtml(originalText.substring(lastIndex, m.start));
            }

            // Fragmento coincidente resaltado
            const matchedContent = escapeHtml(originalText.substring(m.start, m.end));
            const categoryClass = `hl-${m.category}`;
            const tooltipTitle = `${m.pattern_name} [${m.start}:${m.end}]`;

            htmlOutput += `<mark class="hl-match ${categoryClass}" title="${escapeHtml(tooltipTitle)}">${matchedContent}</mark>`;
            lastIndex = m.end;
        }

        // Fragmento final de texto normal
        if (lastIndex < originalText.length) {
            htmlOutput += escapeHtml(originalText.substring(lastIndex));
        }

        highlightedTextBox.innerHTML = htmlOutput;
    }

    function renderDetectedMatchesList(matches) {
        detectedMatchesList.innerHTML = '';

        if (!matches || matches.length === 0) {
            detectedMatchesList.innerHTML = `
                <div class="empty-state" style="padding: 16px;">
                    <p class="empty-text" style="font-size: 0.78rem;">No se detectaron los indicadores definidos</p>
                    <p class="empty-subtext" style="font-size: 0.68rem;">El texto analizado no activó ninguna de las 10 expresiones regulares configuradas.</p>
                </div>
            `;
            return;
        }

        matches.forEach((m, idx) => {
            const item = document.createElement('div');
            item.className = `match-item-card cat-${m.category}`;

            item.innerHTML = `
                <div class="match-item-header">
                    <span class="match-item-name">${escapeHtml(m.pattern_name)}</span>
                    <span class="match-span-badge">Índice: [${m.start} : ${m.end}]</span>
                </div>
                <div class="match-item-slice">"${escapeHtml(m.matched_text)}"</div>
                <div class="match-item-explanation">${escapeHtml(m.explanation)}</div>
            `;

            detectedMatchesList.appendChild(item);
        });
    }

    // -------------------------------------------------------------------------
    // LABORATORIO REGEX (SIS120 DIDÁCTICA)
    // -------------------------------------------------------------------------
    function setupLabPatterns() {
        if (!patternSelect || !currentPatterns.length) return;

        patternSelect.innerHTML = '';
        currentPatterns.forEach((p, index) => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = `Patrón ${index + 1}: ${p.name}`;
            patternSelect.appendChild(opt);
        });

        patternSelect.addEventListener('change', () => {
            displaySelectedLabPattern(patternSelect.value);
        });

        // Mostrar el primero por defecto
        displaySelectedLabPattern(currentPatterns[0].id);
    }

    function displaySelectedLabPattern(patternId) {
        const p = currentPatterns.find(item => item.id === patternId);
        if (!p) return;

        labPatternCategory.textContent = p.category_label || p.category;
        labPatternName.textContent = p.name;
        labPatternRegex.textContent = `r'${p.regex}'`;
        labPatternFlags.textContent = `Modo compilación: ${p.flags_desc}`;
        labPatternExplanation.textContent = p.explanation;

        // Renderizar operadores
        labOperatorsTable.innerHTML = '';
        if (p.operators && p.operators.length) {
            p.operators.forEach(op => {
                const row = document.createElement('div');
                row.className = 'op-row';
                row.innerHTML = `
                    <span class="op-symbol">${escapeHtml(op.symbol)}</span>
                    <span class="op-meaning">${escapeHtml(op.meaning)}</span>
                `;
                labOperatorsTable.appendChild(row);
            });
        }

        // Configurar botones de ejemplos editables
        btnSampleMatch.onclick = () => {
            labTestInput.value = p.sample_match;
            runLabTest(p.id, p.sample_match);
        };

        btnSampleNoMatch.onclick = () => {
            labTestInput.value = p.sample_nomatch;
            runLabTest(p.id, p.sample_nomatch);
        };

        // Resetear resultado del laboratorio
        labResultBox.style.display = 'none';
        labTestInput.value = p.sample_match;
    }

    btnCopyRegex?.addEventListener('click', () => {
        const textToCopy = labPatternRegex.textContent;
        navigator.clipboard.writeText(textToCopy).then(() => {
            showToast('Expresión regular copiada al portapapeles', 'info');
        }).catch(() => {
            showToast('No se pudo copiar automáticamente', 'warning');
        });
    });

    btnRunLabTest?.addEventListener('click', () => {
        const patternId = patternSelect.value;
        const text = labTestInput.value;
        runLabTest(patternId, text);
    });

    async function runLabTest(patternId, text) {
        labResultBox.style.display = 'block';
        labResultStatus.className = 'lab-result-status';
        labResultStatus.textContent = 'Consultando a Python re...';
        labResultContent.innerHTML = '';

        try {
            const response = await fetch('/api/test-pattern', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pattern_id: patternId, text: text })
            });

            const data = await response.json();

            if (data.has_match) {
                labResultStatus.className = 'lab-result-status match-yes';
                labResultStatus.textContent = `🟢 COINCIDENCIA DETECTADA (${data.matches_count} hallazgo${data.matches_count > 1 ? 's' : ''})`;

                let detailsHtml = '<div style="margin-top: 6px; display: flex; flex-direction: column; gap: 6px;">';
                data.matches.forEach((m, idx) => {
                    detailsHtml += `
                        <div style="background: rgba(0,0,0,0.4); padding: 6px 8px; border-radius: 6px;">
                            <strong>Fragmento #${idx + 1}:</strong> <code class="code-inline">${escapeHtml(m.matched_text)}</code>
                            <br><small style="color: #94a3b8;">Posición [start:end]: [${m.start} : ${m.end}]</small>
                        </div>
                    `;
                });
                detailsHtml += '</div>';

                labResultContent.innerHTML = detailsHtml;
            } else {
                labResultStatus.className = 'lab-result-status match-no';
                labResultStatus.textContent = '⚪ SIN COINCIDENCIAS';
                labResultContent.innerHTML = `
                    <p style="color: #94a3b8; font-size: 0.72rem; margin-top: 4px;">
                        El motor <code class="code-inline">re</code> de Python no encontró subcadenas que satisfagan la expresión regular seleccionada. La cadena no pertenece al lenguaje regular reconocido por este autómata.
                    </p>
                `;
            }
        } catch (error) {
            console.error('Error en test de laboratorio:', error);
            labResultStatus.textContent = 'Error al ejecutar prueba';
            labResultContent.textContent = error.message;
        }
    }

    // -------------------------------------------------------------------------
    // HISTORIAL DE SESIÓN (LOCALSTORAGE)
    // -------------------------------------------------------------------------
    const STORAGE_KEY = 'sms_shield_history_v1';

    function getHistoryFromStorage() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveToHistory(analysisResult) {
        const history = getHistoryFromStorage();
        const now = new Date();
        const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

        const entry = {
            id: 'hist-' + Date.now(),
            time: timeStr,
            text: analysisResult.text,
            title: analysisResult.classification.title,
            severity: analysisResult.classification.severity,
            categories_count: analysisResult.categories_count,
            total_matches: analysisResult.total_matches,
            resultData: analysisResult
        };

        history.unshift(entry);
        // Limitar a los 15 más recientes
        if (history.length > 15) history.pop();

        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        } catch (e) {
            console.warn('LocalStorage lleno o no disponible');
        }
    }

    function renderHistory() {
        if (!historyList) return;
        const history = getHistoryFromStorage();

        if (history.length === 0) {
            historyList.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📭</span>
                    <p class="empty-text">Aún no has analizado mensajes en esta sesión.</p>
                    <p class="empty-subtext">Analiza un mensaje desde la bandeja o el analizador para conservarlo en esta lista.</p>
                </div>
            `;
            return;
        }

        historyList.innerHTML = '';
        history.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';

            let badgeClass = 'badge-type-normal';
            if (item.severity === 'safe') badgeClass = 'badge-safe';
            if (item.severity === 'warning') badgeClass = 'badge-warning';
            if (item.severity === 'danger') badgeClass = 'badge-danger';

            card.innerHTML = `
                <div class="history-header-row">
                    <span class="history-badge ${badgeClass}">${escapeHtml(item.title)}</span>
                    <span class="history-time">${escapeHtml(item.time)}</span>
                </div>
                <p class="history-snippet">${escapeHtml(item.text)}</p>
                <div class="history-stats">
                    ${item.categories_count} categoría(s) • ${item.total_matches} coincidencia(s)
                </div>
            `;

            card.addEventListener('click', () => {
                customMessageInput.value = item.text;
                updateCharCounter();
                switchTab('viewAnalyze');
                renderAnalysisResults(item.resultData);
                showToast('Análisis recuperado del historial', 'info');
            });

            historyList.appendChild(card);
        });
    }

    btnClearHistory?.addEventListener('click', () => {
        if (confirm('¿Deseas vaciar el historial de análisis de esta sesión?')) {
            localStorage.removeItem(STORAGE_KEY);
            renderHistory();
            showToast('Historial vaciado', 'info');
        }
    });

    // -------------------------------------------------------------------------
    // CONTROLES EXTERNOS Y MODAL DE GUÍA
    // -------------------------------------------------------------------------
    toggleFrameBtn?.addEventListener('click', () => {
        smartphoneFrame.classList.toggle('expanded-view');
        const isExpanded = smartphoneFrame.classList.contains('expanded-view');
        frameToggleText.textContent = isExpanded ? 'Vista Celular' : 'Vista Completa';
    });

    quickHelpBtn?.addEventListener('click', () => {
        guideModal.style.display = 'flex';
    });

    guideCloseBtn?.addEventListener('click', () => {
        guideModal.style.display = 'none';
    });

    guideOkBtn?.addEventListener('click', () => {
        guideModal.style.display = 'none';
    });

    guideModal?.addEventListener('click', (e) => {
        if (e.target === guideModal) guideModal.style.display = 'none';
    });

    // Iniciar carga de datos
    loadInitialData();
});
