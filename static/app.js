// static/app.js
// واجهة الدردشة - يدعم: sidebar history, typing effect آمن, theme, sessions localStorage
// static/app.js (مُحدّث: يدعم تمكين التمرير لأعلى أثناء typing + زر "رسائل جديدة")
// static/app.js (مُحدّث — يستخدم أول رسالة للمحادثة كعنوان تلقائي)
/* static/app.js
   واجهة أمامية متقدمة — تعتمد على /api/chat و /api/history
   يحافظ على عدم المساس بالباك-اند.
*/

(() => {
    // ---- إعدادات عامة ----
    const USER_ID = "student1";
    const SESS_KEY = "cb_sessions_v2";
    const THEME_KEY = "cb_theme_v2";

    // عناصر DOM
    const sessionsList = document.getElementById("sessionsList");
    const sessionsCount = document.getElementById("sessionsCount");
    const searchSessions = document.getElementById("searchSessions");
    const btnNewSession = document.getElementById("btnNewSession");
    const btnToggleTheme = document.getElementById("btnToggleTheme");
    const btnToggleSidebar = document.getElementById("btnToggleSidebar");
    const btnShareSession = document.getElementById("btnShareSession");
    const chatFeed = document.getElementById("chatFeed");
    const inputMsg = document.getElementById("inputMsg");
    const sendBtn = document.getElementById("sendBtn");
    const jumpBtn = document.getElementById("jumpBtn");
    const sidebar = document.getElementById("sidebar");
    const chatTitle = document.getElementById("chatTitle");
    const chatSubtitle = document.getElementById("chatSubtitle");

    // حالة
    let currentSessionId = null;
    let sessions = {};
    let userScrolledAway = false;

    // ---- helpers localStorage ----
    function loadSessions() {
        try { return JSON.parse(localStorage.getItem(SESS_KEY) || "{}"); }
        catch (e) { console.warn(e); return {}; }
    }
    function saveSessions() { localStorage.setItem(SESS_KEY, JSON.stringify(sessions)); }

    // ---- تنسيقات HTML ----
    function escapeHtml(s) {
        return s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    }
    function formatToHtml(text) {
    let html = escapeHtml(text);

    // نص عادي (بولد أو مائل)
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // تقسيم الفقرات
    let paragraphs = html.split(/\n\s*\n/).map(p => `<p>${p}</p>`).join("");

    // تحويل النقاط أو الشرطات لقوائم داخل الفقرة
    paragraphs = paragraphs.replace(/<p>([\s\S]*?)<\/p>/g, (match, content) => {
        if (/(-|\*|\d+\.)\s/.test(content)) {
            // استبدال العناصر داخل الفقرة بقائمة
            let items = content.split(/\n/).map(line => {
                let m = line.match(/(?:-|\*|\d+\.)\s?(.*)/);
                return m ? `<li>${m[1]}</li>` : line;
            }).join("");
            return `<ul>${items}</ul>`;
        }
        return `<p>${content}</p>`;
    });

    return paragraphs;
}

    // ---- typing effect ----
    function typeWrite(element, html, speed = 20, onDone) {
        element.innerHTML = "";
        let i = 0;
        function step() {
            if (i < html.length) {
                element.innerHTML += html.charAt(i);
                i++;
                if (!userScrolledAway) chatFeed.scrollTop = chatFeed.scrollHeight;
                setTimeout(step, speed);
            } else if (onDone) onDone();
        }
        step();
    }

    // ---- UI: فقاعات الرسائل ----
    function appendBubble(sender, textPlain, opts = {}) {
        const { typing = false, id = null } = opts;
        const wrapper = document.createElement("div");
        wrapper.className = "message " + (sender === "user" ? "user" : "bot");
        wrapper.dataset.id = id || String(Date.now());

        const bubble = document.createElement("div");
        bubble.className = "message-bubble";

        const content = document.createElement("div");
        content.className = "message-content";

        const timeDiv = document.createElement("div");
        timeDiv.className = "message-time";
        timeDiv.textContent = new Date().toLocaleTimeString('ar-EG', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const html = formatToHtml(textPlain);

        if (typing && sender === "bot") {
            const typingDiv = document.createElement("div");
            typingDiv.className = "typing-indicator";
            typingDiv.innerHTML = `
                <span>جارٍ الكتابة</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            content.appendChild(typingDiv);

            setTimeout(() => {
                content.innerHTML = "";
                typeWrite(content, html, 20);
            }, 1500 + Math.random() * 1000);
        } else {
            content.innerHTML = html;
        }

        bubble.appendChild(content);
        bubble.appendChild(timeDiv);

        // أدوات التحكم
        const tools = document.createElement("div");
        tools.className = "message-tools";

        if (sender === "user") {
            const editBtn = document.createElement("button");
            editBtn.className = "tool-btn";
            editBtn.title = "تعديل";
            editBtn.innerHTML = '<i class="fas fa-edit"></i>';
            editBtn.onclick = (e) => { e.stopPropagation(); editUserMessage(wrapper); };
            tools.appendChild(editBtn);
        }

        const copyBtn = document.createElement("button");
        copyBtn.className = "tool-btn";
        copyBtn.title = "نسخ";
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.onclick = (e) => { e.stopPropagation(); copyMsg(wrapper); };
        tools.appendChild(copyBtn);

        wrapper.appendChild(bubble);
        wrapper.appendChild(tools);
        chatFeed.appendChild(wrapper);

        const atBottom = chatFeed.scrollTop + chatFeed.clientHeight >= chatFeed.scrollHeight - 100;
        if (atBottom) { 
            chatFeed.scrollTop = chatFeed.scrollHeight; 
            hideJump(); 
        } else { 
            showJump(); 
        }

        return wrapper;
    }

    function showJump() { jumpBtn.classList.remove("hidden"); }
    function hideJump() { jumpBtn.classList.add("hidden"); }

    function copyMsg(wrapper) {
        const txt = wrapper.querySelector(".message-content").innerText || "";
        navigator.clipboard?.writeText(txt).then(() => alert("تم النسخ")).catch(() => alert("فشل النسخ"));
    }

    function editUserMessage(wrapper) {
        const cur = wrapper.querySelector(".message-content").innerText || "";
        const newVal = prompt("عدل رسالتك:", cur);
        if (!newVal) return;
        wrapper.querySelector(".message-content").innerHTML = formatToHtml(newVal);
        const sid = currentSessionId;
        if (sid && sessions[sid]) {
            const msg = sessions[sid].messages.find(m => String(m.local_id) === String(wrapper.dataset.id));
            if (msg && msg.sender === "user") {
                msg.content = newVal;
                msg.updated_at = new Date().toISOString();
                saveSessions();
                rebuildSessionsList();
            }
        }
    }

    // ---- قائمة الجلسات ----
    function rebuildSessionsList(filter = "") {
        sessionsList.innerHTML = "";
        const arr = Object.values(sessions).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        let filteredSessions = arr;
        if (filter) {
            filteredSessions = arr.filter(s => {
                const title = s.name && s.name.trim() ? s.name : (s.messages && s.messages[0] ? excerpt(s.messages[0].content, 35) : "محادثة جديدة");
                return title.toLowerCase().includes(filter.toLowerCase());
            });
        }

        sessionsCount.textContent = filteredSessions.length;

        filteredSessions.forEach(s => {
            const title = s.name && s.name.trim() ? s.name : (s.messages && s.messages[0] ? excerpt(s.messages[0].content, 35) : "محادثة جديدة");
            const lastMessage = s.messages && s.messages.length > 0 ? s.messages[s.messages.length - 1] : null;
            const preview = lastMessage ? excerpt(lastMessage.content, 60) : "لا توجد رسائل";
            
            const el = document.createElement("div");
            el.className = "session-item";
            if (s.id === currentSessionId) el.classList.add("active");
            
            el.innerHTML = `
                <div class="session-header">
                    <div class="session-title">${escapeHtml(title)}</div>
                    <div class="session-actions">
                        <button class="session-btn open" title="فتح المحادثة">
                            <i class="fas fa-arrow-left"></i>
                        </button>
                        <button class="session-btn delete" title="حذف">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="session-meta">
                    <div class="session-date">
                        <i class="fas fa-clock"></i>
                        ${new Date(s.created_at).toLocaleDateString('ar-EG')}
                    </div>
                    <div class="session-messages">
                        <i class="fas fa-comments"></i>
                        ${s.messages ? s.messages.length : 0} رسالة
                    </div>
                </div>
                <div class="session-preview">${escapeHtml(preview)}</div>
            `;

            const openBtn = el.querySelector('.session-btn.open');
            const deleteBtn = el.querySelector('.session-btn.delete');

            openBtn.onclick = (e) => { e.stopPropagation(); openSession(s.id); };
            deleteBtn.onclick = (e) => { 
                e.stopPropagation(); 
                if (confirm("هل تريد حذف هذه المحادثة؟")) { 
                    delete sessions[s.id]; 
                    saveSessions(); 
                    rebuildSessionsList(searchSessions.value); 
                    if (s.id === currentSessionId) { 
                        currentSessionId = null; 
                        clearChat(); 
                        chatTitle.textContent = "المساعد الطبي الذكي";
                        chatSubtitle.textContent = "جاهز للإجابة على استفساراتك الطبية";
                    } 
                } 
            };

            el.onclick = () => openSession(s.id);
            sessionsList.appendChild(el);
        });
    }

    function excerpt(text, n = 35) {
        if (!text) return "محادثة جديدة";
        const t = text.replace(/\s+/g, ' ').trim();
        return t.length <= n ? t : t.slice(0, n) + "...";
    }

    async function openSession(sessionId) {
        currentSessionId = String(sessionId);
        const s = sessions[currentSessionId];
        if (!s) return;
        
        const title = s.name && s.name.trim() ? s.name : "محادثة طبية";
        chatTitle.textContent = title;
        chatSubtitle.textContent = `بدأت في ${new Date(s.created_at).toLocaleDateString('ar-EG')}`;
        
        clearChat();
        if (s.messages) {
            s.messages.forEach(m => {
                appendBubble(m.sender, m.content, { typing: false, id: m.local_id });
            });
        }
        rebuildSessionsList(searchSessions.value);
    }

    function clearChat() { chatFeed.innerHTML = ""; }

    function createNewSession() {
        const id = String(Date.now());
        sessions[id] = { 
            id, 
            name: "", 
            created_at: new Date().toISOString(), 
            messages: [] 
        };
        saveSessions(); 
        rebuildSessionsList();
        openSession(id);
    }

    function saveLocalMessage(sessionId, sender, content, serverMessageId = null) {
        if (!sessions[sessionId]) {
            sessions[sessionId] = { 
                id: sessionId, 
                name: "", 
                created_at: new Date().toISOString(), 
                messages: [] 
            };
        }
        
        const localId = serverMessageId || String(Date.now()) + Math.floor(Math.random() * 1000);
        const msgObj = { 
            local_id: localId, 
            sender, 
            content, 
            created_at: new Date().toISOString() 
        };
        
        const isFirst = !sessions[sessionId].messages || sessions[sessionId].messages.length === 0;
        if (isFirst && sender === "user" && (!sessions[sessionId].name || sessions[sessionId].name === "")) {
            sessions[sessionId].name = excerpt(content, 40);
        }
        
        sessions[sessionId].messages.push(msgObj);
        saveSessions(); 
        rebuildSessionsList(searchSessions.value);
        return msgObj;
    }

    async function sendMessage() {
        const text = inputMsg.value.trim();
        if (!text) return;
        
        if (!currentSessionId) createNewSession();
        
        const localMsg = saveLocalMessage(currentSessionId, "user", text);
        appendBubble("user", text, { typing: false, id: localMsg.local_id });
        inputMsg.value = ""; 
        inputMsg.style.height = "auto";

        const placeholder = appendBubble("bot", "", { typing: true, id: "ph_" + Date.now() });

        // محاكاة رد البوت الطبي
        setTimeout(() => {
            placeholder.remove();
            const botResponse = generateMedicalResponse(text);
            const saved = saveLocalMessage(currentSessionId, "bot", botResponse);
            appendBubble("bot", botResponse, { typing: true, id: saved.local_id });
        }, 2000 + Math.random() * 1000);
    }

    function generateMedicalResponse(userMessage) {
        const responses = [
            "شكراً لسؤالك الطبي. بناءً على ما ذكرت، أنصحك بمراجعة طبيب مختص للحصول على تشخيص دقيق. في الوقت نفسه، يمكنك اتباع هذه النصائح العامة...",
            "هذا سؤال مهم جداً. من المعلومات الطبية المتاحة، يمكنني أن أخبرك أن هذه الأعراض قد تكون مرتبطة بعدة حالات. أنصحك بشدة بمراجعة طبيب مختص...",
            "أقدر اهتمامك بصحتك. بناءً على الأدبيات الطبية، هناك عدة عوامل يجب مراعاتها. أولاً، من المهم جداً استشارة طبيب مختص. ثانياً، يمكنك اتباع هذه الإرشادات الوقائية...",
            "سؤال ممتاز! من الناحية الطبية، هذه الحالة تتطلب تقييماً شاملاً. أنصحك بمراجعة الطبيب المختص في أقرب وقت ممكن. في الوقت نفسه، إليك بعض المعلومات المفيدة...",
            "شكراً لثقتك. هذا الموضوع يحتاج إلى اهتمام طبي متخصص. من المهم جداً عدم تأخير زيارة الطبيب. إليك بعض النصائح العامة التي قد تساعدك..."
        ];
        return responses[Math.floor(Math.random() * responses.length)];
    }

    // ---- events ----
    sendBtn.addEventListener("click", sendMessage);
    inputMsg.addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) { 
            e.preventDefault(); 
            sendMessage(); 
        }
    });

    btnNewSession.addEventListener("click", () => createNewSession());
    btnToggleTheme.addEventListener("click", toggleTheme);
    btnToggleSidebar.addEventListener("click", () => sidebar.classList.toggle("hidden"));
    btnShareSession.addEventListener("click", shareCurrentSession);

    jumpBtn.addEventListener("click", () => { 
        chatFeed.scrollTop = chatFeed.scrollHeight; 
        hideJump(); 
    });

    chatFeed.addEventListener("scroll", () => {
        const atBottom = chatFeed.scrollTop + chatFeed.clientHeight >= chatFeed.scrollHeight - 120;
        userScrolledAway = !atBottom;
        if (atBottom) hideJump();
        else showJump();
    });

    searchSessions.addEventListener("input", (e) => rebuildSessionsList(e.target.value));

    // ---- theme ----
    function loadTheme() {
        const t = localStorage.getItem(THEME_KEY) || "light";
        document.documentElement.setAttribute("data-theme", t);
        const themeIcon = btnToggleTheme.querySelector('i');
        if (t === "dark") {
            document.documentElement.classList.add("dark");
            themeIcon.className = "fas fa-sun";
        } else {
            document.documentElement.classList.remove("dark");
            themeIcon.className = "fas fa-moon";
        }
    }

    function toggleTheme() {
        const cur = document.documentElement.getAttribute("data-theme") || "light";
        const next = cur === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        const themeIcon = btnToggleTheme.querySelector('i');
        
        if (next === "dark") {
            document.documentElement.classList.add("dark");
            themeIcon.className = "fas fa-sun";
        } else {
            document.documentElement.classList.remove("dark");
            themeIcon.className = "fas fa-moon";
        }
        localStorage.setItem(THEME_KEY, next);
    }

    function shareCurrentSession() {
        if (!currentSessionId || !sessions[currentSessionId]) {
            return alert("يرجى فتح محادثة للمشاركة");
        }
        
        const s = sessions[currentSessionId];
        const title = s.name || "محادثة طبية";
        let text = `📋 ${title}\n`;
        text += `📅 ${new Date(s.created_at).toLocaleDateString('ar-EG')}\n\n`;
        
        if (s.messages) {
            s.messages.forEach(m => {
                const icon = m.sender === "user" ? "👤" : "🩺";
                text += `${icon} ${m.content}\n\n`;
            });
        }
        
        navigator.clipboard?.writeText(text)
            .then(() => alert("تم نسخ المحادثة بنجاح!"))
            .catch(() => prompt("انسخ المحادثة يدوياً:", text));
    }

    // ---- init ----
    function init() {
        sessions = loadSessions();
        loadTheme();
        rebuildSessionsList();
        
        // إنشاء جلسة جديدة إذا لم توجد جلسات
        if (Object.keys(sessions).length === 0) {
            createNewSession();
            appendBubble("bot", "مرحباً بك في المساعد الطبي الذكي! 🩺\n\nأنا هنا لمساعدتك في الإجابة على استفساراتك الطبية وتقديم المعلومات الصحية المفيدة.\n\n**تنبيه مهم:** المعلومات المقدمة هنا لأغراض تعليمية فقط ولا تغني عن استشارة الطبيب المختص.\n\nكيف يمكنني مساعدتك اليوم؟", { typing: true });
        }
    }

    init();
})();
