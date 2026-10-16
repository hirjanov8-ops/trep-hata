const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
if (tg) { tg.expand(); tg.ready(); }

let soundEnabled = true;
let audioCtx = null;

function initAudio() {
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) audioCtx = new AudioContext();
  }
  if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
}

function haptic(type = "light") {
  try {
    if (tg && tg.HapticFeedback) {
      if (type === "success" || type === "error" || type === "warning") {
        tg.HapticFeedback.notificationOccurred(type);
      } else {
        tg.HapticFeedback.impactOccurred(type);
      }
    } else if (navigator.vibrate) {
      navigator.vibrate(type === "heavy" ? 60 : 20);
    }
  } catch (e) {}
}

function playSound(effect) {
  if (!soundEnabled) return;
  try {
    initAudio();
    if (!audioCtx) return;
    const now = audioCtx.currentTime;

    if (effect === "tick") {
      const osc = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(680, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.035);
      g.gain.setValueAtTime(0.12, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.035);
      osc.connect(g); g.connect(audioCtx.destination);
      osc.start(now); osc.stop(now + 0.04);
    } else if (effect === "win") {
      [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);
        g.gain.setValueAtTime(0.18, now + idx * 0.08);
        g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.25);
        osc.connect(g); g.connect(audioCtx.destination);
        osc.start(now + idx * 0.08); osc.stop(now + idx * 0.08 + 0.26);
      });
      haptic("success");
    } else if (effect === "fail") {
      [300, 220, 150].forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(freq, now + idx * 0.12);
        g.gain.setValueAtTime(0.15, now + idx * 0.12);
        g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.12 + 0.22);
        osc.connect(g); g.connect(audioCtx.destination);
        osc.start(now + idx * 0.12); osc.stop(now + idx * 0.12 + 0.24);
      });
      haptic("error");
    } else if (effect === "click") {
      const osc = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(420, now);
      g.gain.setValueAtTime(0.08, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.03);
      osc.connect(g); g.connect(audioCtx.destination);
      osc.start(now); osc.stop(now + 0.035);
      haptic("light");
    }
  } catch (e) {}
}

function toggleSound() {
  soundEnabled = !soundEnabled;
  document.getElementById("btn-sound").innerText = soundEnabled ? "🔊 Звук" : "🔇 Выкл";
  if (soundEnabled) playSound("click");
}

// ГЕНЕРАТОР ИКОНОК И СЛОЁВ
function makeItemIcon(slot, c1, c2, label, special = "") {
  if (special === "coins") {
    return `<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="24" fill="#fbbf24" stroke="#fef08a" stroke-width="3"/><circle cx="32" cy="32" r="18" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="4 2"/><text x="32" y="37" font-size="13" text-anchor="middle" fill="#000" font-weight="900">${label}</text></svg>`;
  }
  if (special === "karas_head") {
    return `<svg viewBox="0 0 64 64"><ellipse cx="32" cy="34" rx="24" ry="18" fill="#0ea5e9" stroke="#bae6fd" stroke-width="2.5"/><polygon points="32,8 22,18 42,18" fill="#0284c7"/><circle cx="20" cy="30" r="5" fill="#fff"/><circle cx="20" cy="30" r="2.5" fill="#000"/><circle cx="44" cy="27" r="4" fill="#fff"/><circle cx="45" cy="26" r="2" fill="#000"/><path d="M22 42 Q32 48 42 42" stroke="#0f172a" stroke-width="3" fill="none"/></svg>`;
  }
  if (special === "karas_tail") {
    return `<svg viewBox="0 0 64 64"><path d="M16 36 Q32 32 44 14 L54 32 L44 52 Q32 38 16 36 Z" fill="#0ea5e9" stroke="#7dd3fc" stroke-width="2.5"/><line x1="28" y1="34" x2="48" y2="24" stroke="#bae6fd" stroke-width="2"/><line x1="28" y1="36" x2="48" y2="44" stroke="#bae6fd" stroke-width="2"/></svg>`;
  }
  if (special === "ptitsa_trusy") {
    return `<svg viewBox="0 0 64 64"><path d="M10 14 H54 L51 48 L39 44 L35 49 L32 34 L28 48 L21 43 L13 48 Z" fill="#fca5a5" stroke="#ef4444" stroke-width="2"/><circle cx="24" cy="28" r="5" fill="#07090e"/><circle cx="42" cy="34" r="4" fill="#07090e"/></svg>`;
  }
  if (special === "kirill_shirt") {
    return `<svg viewBox="0 0 64 64"><path d="M16 14 L25 10 H39 L48 14 L56 26 L47 33 L44 25 V50 L37 46 L31 51 L25 46 L20 50 V25 L17 33 L8 26 Z" fill="#f8fafc" stroke="#94a3b8" stroke-width="2"/><circle cx="27" cy="30" r="4" fill="#07090e"/><circle cx="38" cy="38" r="5" fill="#07090e"/></svg>`;
  }
  if (special === "sanya_robe") {
    return `<svg viewBox="0 0 64 64"><path d="M16 12 L26 9 H38 L48 12 L56 28 L46 34 L44 24 V56 H20 V24 L18 34 L8 28 Z" fill="#1d4ed8" stroke="#f59e0b" stroke-width="2.5"/><text x="32" y="48" font-size="7" text-anchor="middle" fill="#fde68a" font-weight="900">CAMEL</text></svg>`;
  }
  if (slot === "head") {
    return `<svg viewBox="0 0 64 64"><path d="M12 44 C12 18 52 18 52 44 Z" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><rect x="8" y="40" width="48" height="7" rx="3" fill="${c2}"/><text x="32" y="35" font-size="9" text-anchor="middle" fill="#fff" font-weight="900">${label}</text></svg>`;
  }
  if (slot === "face") {
    return `<svg viewBox="0 0 64 64"><rect x="10" y="22" width="19" height="15" rx="4" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><rect x="35" y="22" width="19" height="15" rx="4" fill="${c1}" stroke="${c2}" stroke-width="2.5"/></svg>`;
  }
  if (slot === "body") {
    return `<svg viewBox="0 0 64 64"><path d="M16 14 L25 10 H39 L48 14 L56 27 L47 33 L44 25 V52 H20 V25 L17 33 L8 27 Z" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><text x="32" y="37" font-size="8" text-anchor="middle" fill="#fff" font-weight="900">${label}</text></svg>`;
  }
  if (slot === "legs") {
    return `<svg viewBox="0 0 64 64"><path d="M14 12 H50 L47 52 H35 L32 28 L29 52 H17 Z" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><text x="32" y="24" font-size="8" text-anchor="middle" fill="#fff" font-weight="900">${label}</text></svg>`;
  }
  if (slot === "feet") {
    return `<svg viewBox="0 0 64 64"><path d="M10 38 Q10 24 24 24 V46 H8 Z M36 38 Q36 24 50 24 V46 H34 Z" fill="${c1}" stroke="${c2}" stroke-width="2.5"/></svg>`;
  }
  return `<svg viewBox="0 0 64 64"><polygon points="32,8 52,24 44,52 20,52 12,24" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><text x="32" y="36" font-size="8" text-anchor="middle" fill="#fff" font-weight="900">${label}</text></svg>`;
}

function makeMannequinLayer(slot, c1, c2, label, special = "") {
  if (special === "karas_head") {
    return `<ellipse cx="100" cy="48" rx="38" ry="28" fill="#0ea5e9" stroke="#bae6fd" stroke-width="2.5"/><polygon points="100,10 86,23 114,23" fill="#0284c7"/><circle cx="84" cy="44" r="7" fill="#fff"/><circle cx="84" cy="44" r="3.5" fill="#000"/><circle cx="116" cy="40" r="5.5" fill="#fff"/><circle cx="118" cy="39" r="2.5" fill="#000"/>`;
  }
  if (special === "karas_tail") {
    return `<path d="M122 178 Q165 168 184 132 L194 172 L178 214 Q152 192 122 178 Z" fill="#0ea5e9" stroke="#7dd3fc" stroke-width="2.5"/>`;
  }
  if (special === "ptitsa_trusy") {
    return `<path d="M66 165 H134 L131 208 L116 202 L109 209 L100 186 L91 208 L81 201 L69 208 Z" fill="#fca5a5" stroke="#ef4444" stroke-width="1.8"/>`;
  }
  if (special === "kirill_shirt") {
    return `<path d="M63 87 H137 L135 170 L120 163 L108 171 L95 164 L80 171 L65 166 Z" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.8"/>`;
  }
  if (special === "sanya_robe") {
    return `<path d="M60 86 H140 L144 236 H56 Z" fill="#1d4ed8" stroke="#f59e0b" stroke-width="2.5"/><text x="100" y="192" font-size="13" text-anchor="middle" fill="#fde68a" font-weight="900">CAMEL 🐗</text>`;
  }
  if (special === "mj_hat") {
    return `<ellipse cx="100" cy="27" rx="44" ry="9" fill="#090d16" stroke="#f8fafc" stroke-width="2"/><path d="M74 27 L80 4 Q100 -2 120 4 L126 27 Z" fill="#090d16" stroke="#f8fafc" stroke-width="2"/>`;
  }
  if (special === "mj_glasses") {
    return `<path d="M75 40 H97 L94 53 Q85 56 77 51 Z M103 40 H125 L123 51 Q115 56 106 53 Z" fill="#0f172a" stroke="#fbbf24" stroke-width="2.5"/>`;
  }
  if (special === "mj_jacket") {
    return `<rect x="62" y="86" width="76" height="86" rx="12" fill="#dc2626" stroke="#fbbf24" stroke-width="2.5"/>`;
  }
  if (special === "mj_pants") {
    return `<path d="M66 166 H134 L130 236 H104 L100 188 L96 236 H70 Z" fill="#090d16" stroke="#fbbf24" stroke-width="1.5"/>`;
  }
  if (special === "mj_shoes") {
    return `<rect x="61" y="252" width="37" height="19" rx="7" fill="#090d16" stroke="#f8fafc" stroke-width="2"/><rect x="102" y="252" width="37" height="19" rx="7" fill="#090d16" stroke="#f8fafc" stroke-width="2"/>`;
  }
  if (special === "mj_glove") {
    return `<circle cx="147" cy="158" r="13" fill="#f8fafc" stroke="#38bdf8" stroke-width="2.5"/>`;
  }
  if (special === "throne_alhan") {
    return `<rect x="46" y="20" width="108" height="260" rx="18" fill="#451a03" stroke="#fbbf24" stroke-width="4"/>`;
  }
  if (slot === "head") {
    return `<path d="M68 38 C68 6 132 6 132 38 Z" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><text x="100" y="28" font-size="9" text-anchor="middle" fill="#fff" font-weight="900">${label}</text>`;
  }
  if (slot === "face") {
    return `<rect x="75" y="39" width="21" height="14" rx="4" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><rect x="104" y="39" width="21" height="14" rx="4" fill="${c1}" stroke="${c2}" stroke-width="2.5"/>`;
  }
  if (slot === "body") {
    return `<rect x="62" y="86" width="76" height="86" rx="14" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><text x="100" y="134" font-size="11" text-anchor="middle" fill="#fff" font-weight="900">${label}</text>`;
  }
  if (slot === "legs") {
    return `<path d="M66 166 H134 L130 246 H104 L100 190 L96 246 H70 Z" fill="${c1}" stroke="${c2}" stroke-width="2"/><text x="100" y="182" font-size="9" text-anchor="middle" fill="#fff" font-weight="900">${label}</text>`;
  }
  if (slot === "feet") {
    return `<rect x="61" y="251" width="37" height="20" rx="8" fill="${c1}" stroke="${c2}" stroke-width="2.5"/><rect x="102" y="251" width="37" height="20" rx="8" fill="${c1}" stroke="${c2}" stroke-width="2.5"/>`;
  }
  return `<path d="M78 88 Q100 132 122 88" fill="none" stroke="${c2}" stroke-width="5" stroke-linecap="round"/><circle cx="100" cy="122" r="12" fill="${c1}" stroke="${c2}" stroke-width="2.5"/>`;
}

// 56 ПРЕДМЕТОВ И ПАЧЕК КОЙНОВ
const RAW_ITEMS = [
  { id: "ptitsa_trusy", name: "Трусы Птицы (порванные семейники)", slot: "legs", rarity: "common", price: 0.2, c1: "#fca5a5", c2: "#ef4444", lbl: "ПТИЦА", spec: "ptitsa_trusy" },
  { id: "kirill_shirt", name: "Порванная белая футболка Кирилла", slot: "body", rarity: "common", price: 0.4, c1: "#f8fafc", c2: "#94a3b8", lbl: "ДЫРЫ", spec: "kirill_shirt" },
  { id: "sanya_robe", name: "Синий халат Жиросана Кэмел", slot: "body", rarity: "epic", price: 4.5, c1: "#1d4ed8", c2: "#f59e0b", lbl: "CAMEL", spec: "sanya_robe" },
  { id: "karas_head", name: "Голова Карася (Мутант из Оби)", slot: "head", rarity: "epic", price: 5.0, c1: "#0ea5e9", c2: "#bae6fd", lbl: "КАРАСЬ", spec: "karas_head" },
  { id: "karas_tail", name: "Чешуйчатый Хвост Карася", slot: "acc", rarity: "epic", price: 4.2, c1: "#0ea5e9", c2: "#7dd3fc", lbl: "ХВОСТ", spec: "karas_tail", isBackLayer: true },

  { id: "mj_hat", name: "Шляпа Майкла Джексона с локонами", slot: "head", rarity: "legendary", price: 8.5, c1: "#090d16", c2: "#f8fafc", lbl: "MJ", spec: "mj_hat", mjSet: true },
  { id: "mj_glasses", name: "Зеркальные Авиаторы Джексона", slot: "face", rarity: "epic", price: 4.0, c1: "#0f172a", c2: "#fbbf24", lbl: "MJ", spec: "mj_glasses", mjSet: true },
  { id: "mj_jacket", name: "Красный Китель Короля Поп-Музыки", slot: "body", rarity: "legendary", price: 9.0, c1: "#dc2626", c2: "#fbbf24", lbl: "MJ", spec: "mj_jacket", mjSet: true },
  { id: "mj_pants", name: "Брюки Билли Джин с белыми носками", slot: "legs", rarity: "epic", price: 4.8, c1: "#090d16", c2: "#fbbf24", lbl: "MJ", spec: "mj_pants", mjSet: true },
  { id: "mj_shoes", name: "Лаковые Лоферы Лунной Походки", slot: "feet", rarity: "epic", price: 5.2, c1: "#090d16", c2: "#f8fafc", lbl: "MJ", spec: "mj_shoes", mjSet: true },
  { id: "mj_glove", name: "Белая Перчатка Джексона со стразами", slot: "acc", rarity: "legendary", price: 8.0, c1: "#f8fafc", c2: "#38bdf8", lbl: "MJ", spec: "mj_glove", mjSet: true },

  { id: "mythic_daily_glove", name: "Мифическая Бриллиантовая Перчатка MJ", slot: "acc", rarity: "mythic", price: 25.0, c1: "#38bdf8", c2: "#fde047", lbl: "25 HC", spec: "mj_glove" },
  { id: "mythic_weekly_throne", name: "Золотой Императорский Трон Алхана", slot: "acc", rarity: "mythic", price: 50.0, c1: "#fbbf24", c2: "#ef4444", lbl: "50 HC", spec: "throne_alhan", isBackLayer: true },

  { id: "coins_1", name: "Горсть мелочи (+1.0 HC)", slot: "coins", rarity: "common", price: 1.0, c1: "#fbbf24", c2: "#d97706", lbl: "+1 HC", spec: "coins" },
  { id: "coins_3", name: "Купюра на шавуху (+3.0 HC)", slot: "coins", rarity: "rare", price: 3.0, c1: "#fbbf24", c2: "#d97706", lbl: "+3 HC", spec: "coins" },
  { id: "coins_7", name: "Заначка в матрасе (+7.0 HC)", slot: "coins", rarity: "epic", price: 7.0, c1: "#fbbf24", c2: "#d97706", lbl: "+7 HC", spec: "coins" },
  { id: "coins_15", name: "Кэшбек от Алхана (+15.0 HC)", slot: "coins", rarity: "legendary", price: 15.0, c1: "#fbbf24", c2: "#d97706", lbl: "+15 HC", spec: "coins" },
  { id: "coins_25", name: "Джекпот Треп Хаты (+25.0 HC)", slot: "coins", rarity: "mythic", price: 25.0, c1: "#fbbf24", c2: "#d97706", lbl: "+25 HC", spec: "coins" },

  { id: "trusy_karasya", name: "Трусы Карася в горошек", slot: "legs", rarity: "common", price: 0.2, c1: "#ef4444", c2: "#ffffff", lbl: "ГОРОХ" },
  { id: "noski_pnya", name: "Дырявые носки Пня", slot: "feet", rarity: "common", price: 0.1, c1: "#475569", c2: "#94a3b8", lbl: "ПЕНЬ" },
  { id: "shlepki_banya", name: "Резиновые сланцы из общаги", slot: "feet", rarity: "common", price: 0.3, c1: "#2563eb", c2: "#93c5fd", lbl: "СЛАНЦЫ" },
  { id: "kepka_gop", name: "Кепка-восьмиклинка с района", slot: "head", rarity: "common", price: 0.3, c1: "#334155", c2: "#cbd5e1", lbl: "КЕПКА" },
  { id: "shapka_banya", name: "Войлочная шапка «Царь Бани»", slot: "head", rarity: "common", price: 0.4, c1: "#d6d3d1", c2: "#ef4444", lbl: "БАНЯ" },
  { id: "paket_head", name: "Пакет Пятёрочки на голову", slot: "head", rarity: "common", price: 0.1, c1: "#ef4444", c2: "#ffffff", lbl: "5-КА" },
  { id: "parik_kirilla", name: "Длинный парик прошлого Кирилла", slot: "head", rarity: "rare", price: 0.9, c1: "#090d16", c2: "#64748b", lbl: "ПАРИК" },
  { id: "kaska_sharaga", name: "Строительная каска с практики", slot: "head", rarity: "rare", price: 1.1, c1: "#f97316", c2: "#fed7aa", lbl: "ТРУД" },
  { id: "bandana_rap", name: "Бандана Трэп-Лорда", slot: "head", rarity: "rare", price: 1.4, c1: "#7c3aed", c2: "#ddd6fe", lbl: "TRAP" },
  { id: "ushanka_zima", name: "Боевая ушанка деда", slot: "head", rarity: "epic", price: 3.2, c1: "#78350f", c2: "#fde68a", lbl: "УШАНКА" },
  { id: "shlem_sultana", name: "Шлем ебучего султана", slot: "head", rarity: "legendary", price: 10.0, c1: "#f59e0b", c2: "#fef08a", lbl: "СУЛТАН" },
  { id: "nimh_alhana", name: "Божественный Нимб Алхана", slot: "head", rarity: "legendary", price: 10.0, c1: "#38bdf8", c2: "#fde047", lbl: "АЛХАН" },

  { id: "ochki_kosye", name: "Косые очки Карася", slot: "face", rarity: "rare", price: 1.2, c1: "#0284c7", c2: "#f43f5e", lbl: "КОСЫЕ" },
  { id: "zub_zoloto", name: "Золотой сколотый зуб Карася", slot: "face", rarity: "rare", price: 1.8, c1: "#fbbf24", c2: "#ffffff", lbl: "ЗУБ" },
  { id: "povyazka_pirat", name: "Пиратская повязка от ракетницы", slot: "face", rarity: "rare", price: 1.5, c1: "#111827", c2: "#ef4444", lbl: "ГЛАЗ" },
  { id: "usy_bati", name: "Густые усы трудовика", slot: "face", rarity: "common", price: 0.5, c1: "#78350f", c2: "#d97706", lbl: "УСЫ" },
  { id: "maska_anon", name: "Маска Взломщика Вайфая", slot: "face", rarity: "epic", price: 3.6, c1: "#e2e8f0", c2: "#ef4444", lbl: "HACK" },
  { id: "ochki_matrix", name: "Очки Архитектора Нейросетей", slot: "face", rarity: "epic", price: 4.4, c1: "#059669", c2: "#6ee7b7", lbl: "AI" },
  { id: "vizor_cyber", name: "Кибер-Визор Жиросана 2077", slot: "face", rarity: "legendary", price: 9.5, c1: "#ec4899", c2: "#38bdf8", lbl: "2077" },

  { id: "mayka_alko", name: "Майка-алкоголичка в горчице", slot: "body", rarity: "common", price: 0.3, c1: "#e2e8f0", c2: "#eab308", lbl: "СОУС" },
  { id: "telnyashka", name: "Тельняшка Рыболова", slot: "body", rarity: "common", price: 0.6, c1: "#1e3a8a", c2: "#ffffff", lbl: "МОРЕ" },
  { id: "hoodie_python", name: "Хакерское худи Сани <Python/>", slot: "body", rarity: "rare", price: 1.7, c1: "#059669", c2: "#6ee7b7", lbl: "CODE" },
  { id: "olymp_90", name: "Олимпийка Adidas с рынка", slot: "body", rarity: "rare", price: 1.9, c1: "#1d4ed8", c2: "#ffffff", lbl: "ТРИ ПОЛОСКИ" },
  { id: "fartuk_omlet", name: "Фартук Шеф-Повара Омлета", slot: "body", rarity: "rare", price: 2.2, c1: "#ea580c", c2: "#fed7aa", lbl: "ОМЛЕТ" },
  { id: "kurtka_jager", name: "Бомбер «Укротитель Ягермейстера»", slot: "body", rarity: "epic", price: 4.8, c1: "#14532d", c2: "#f59e0b", lbl: "JÄGER" },
  { id: "shuba_boss", name: "Леопардовая шуба Сутенёра", slot: "body", rarity: "legendary", price: 10.0, c1: "#b45309", c2: "#fde047", lbl: "PIMP" },

  { id: "triko_koleni", name: "Трико с вытянутыми коленями", slot: "legs", rarity: "common", price: 0.4, c1: "#1e293b", c2: "#64748b", lbl: "ТРИКО" },
  { id: "shorty_plyazh", name: "Пляжные шорты охотника на самок", slot: "legs", rarity: "rare", price: 1.3, c1: "#06b6d4", c2: "#fde047", lbl: "ПЛЯЖ" },
  { id: "cargo_camo", name: "Камуфляжные карго для походов в КБ", slot: "legs", rarity: "rare", price: 2.0, c1: "#3f6212", c2: "#a3e635", lbl: "КБ" },
  { id: "jeans_vintage", name: "Широкие трубы Трэп-Хаты", slot: "legs", rarity: "epic", price: 3.8, c1: "#1e40af", c2: "#93c5fd", lbl: "WIDE" },
  { id: "shtany_gold", name: "Золотые шаровары Олигарха", slot: "legs", rarity: "legendary", price: 9.2, c1: "#d97706", c2: "#fef08a", lbl: "VIP" },

  { id: "tapki_deda", name: "Войлочные тапки «Прощай молодость»", slot: "feet", rarity: "common", price: 0.3, c1: "#57534e", c2: "#a8a29e", lbl: "ТАПКИ" },
  { id: "crocs_sport", name: "Кроксы в спортивном режиме 4WD", slot: "feet", rarity: "rare", price: 1.6, c1: "#10b981", c2: "#ecfdf5", lbl: "4WD" },
  { id: "tyagi_barhat", name: "Бархатные тяги (Кефтеме)", slot: "feet", rarity: "epic", price: 4.1, c1: "#7f1d1d", c2: "#fca5a5", lbl: "ТЯГИ" },
  { id: "boots_gold", name: "Кроссовки Алхана с подсветкой", slot: "feet", rarity: "legendary", price: 8.8, c1: "#f59e0b", c2: "#38bdf8", lbl: "NEON" },

  { id: "ershik_acc", name: "Боевой ёршик правосудия", slot: "acc", rarity: "common", price: 0.3, c1: "#64748b", c2: "#f8fafc", lbl: "ЁРШ" },
  { id: "butylka_jager", name: "Личная фляга ледяного Ягеря", slot: "acc", rarity: "rare", price: 2.1, c1: "#14532d", c2: "#f97316", lbl: "56 ТРАВ" },
  { id: "stakan_whiskey", name: "Бокал Виски со льдом Кирилла", slot: "acc", rarity: "rare", price: 2.3, c1: "#b45309", c2: "#fde68a", lbl: "WHISKEY" },
  { id: "skovoroda_gold", name: "Золотая сковорода с Омлетом Карася", slot: "acc", rarity: "epic", price: 5.5, c1: "#1f2937", c2: "#fbbf24", lbl: "ОМЛЕТ" },
  { id: "cep_jacksona", name: "Толстая Золотая Цепь Джексона", slot: "acc", rarity: "legendary", price: 10.0, c1: "#fbbf24", c2: "#fef08a", lbl: "GOLD" }
];

const ITEMS_DB = {};
RAW_ITEMS.forEach(it => {
  ITEMS_DB[it.id] = {
    ...it,
    iconSvg: makeItemIcon(it.slot, it.c1, it.c2, it.lbl, it.spec || ""),
    mannequinSvg: it.slot === "coins" ? "" : makeMannequinLayer(it.slot, it.c1, it.c2, it.lbl, it.spec || "")
  };
});

const WEARABLE_SORTED = Object.values(ITEMS_DB).filter(i => i.slot !== "coins").sort((a, b) => a.price - b.price);

const CASES_DB = [
  { id: "c_pyaterochka", name: "Пакет из Пятёрочки", price: 8, color: "#ef4444", items: ["ptitsa_trusy", "noski_pnya", "paket_head", "trusy_karasya", "mayka_alko", "ershik_acc", "coins_1", "tapki_deda"] },
  { id: "c_sharaga", name: "Рюкзак из Шараги", price: 16, color: "#3b82f6", items: ["kirill_shirt", "shlepki_banya", "kepka_gop", "triko_koleni", "usy_bati", "kaska_sharaga", "coins_1", "coins_3", "hoodie_python"] },
  { id: "c_karas", name: "Садок Карася", price: 28, color: "#0ea5e9", items: ["trusy_karasya", "telnyashka", "ochki_kosye", "zub_zoloto", "povyazka_pirat", "shorty_plyazh", "fartuk_omlet", "karas_tail", "karas_head", "coins_3"] },
  { id: "c_jirosan", name: "Гардероб Жиросана", price: 35, color: "#10b981", items: ["hoodie_python", "butylka_jager", "ochki_matrix", "sanya_robe", "kurtka_jager", "vizor_cyber", "coins_3", "coins_7"] },
  { id: "c_jackson", name: "Гримёрка Майкла Джексона", price: 48, color: "#a855f7", items: ["parik_kirilla", "stakan_whiskey", "mj_glasses", "mj_pants", "mj_shoes", "mj_glove", "mj_hat", "mj_jacket", "cep_jacksona"] },
  { id: "c_bar", name: "Пятничный Бухич", price: 40, color: "#f97316", items: ["cargo_camo", "butylka_jager", "stakan_whiskey", "kurtka_jager", "skovoroda_gold", "tyagi_barhat", "coins_7", "coins_15"] },
  { id: "c_cash", name: "Воровской Общак", price: 30, color: "#eab308", items: ["coins_1", "coins_3", "coins_7", "coins_15", "coins_25", "shtany_gold", "cep_jacksona"] },
  { id: "c_alhan", name: "Святилище Алхана", price: 85, color: "#fbbf24", items: ["sanya_robe", "karas_head", "mj_hat", "mj_jacket", "shlem_sultana", "nimh_alhana", "shuba_boss", "cep_jacksona", "boots_gold", "coins_15"] }
];

const ACHIEVEMENTS_DB = [
  { id: "a_reg", title: "Прописка в Треп Хате", desc: "Прошёл регистрацию и получил стартовые 5 HC", icon: "🏠", check: s => s.registered },
  { id: "a_ptitsa", title: "Позор Птицы", desc: "Выбил или надел порванные семейники Птицы", icon: "🩲", check: s => s.inventory.includes("ptitsa_trusy") || s.equipped.legs === "ptitsa_trusy" },
  { id: "a_kirill_t", title: "Белая Рвань", desc: "Добыл порванную белую футболку Кирилла", icon: "👕", check: s => s.inventory.includes("kirill_shirt") },
  { id: "a_camel", title: "Барон Кэмел", desc: "Выбил Синий халат Жиросана Кэмел", icon: "🧥", check: s => s.inventory.includes("sanya_robe") },
  { id: "a_karas_full", title: "Ихтиандр из Шараги", desc: "Собрал Голову Карася и Хвост Карася", icon: "🐟", check: s => s.inventory.includes("karas_head") && s.inventory.includes("karas_tail") },
  { id: "a_mj_1", title: "Лунная Походка: Старт", desc: "Выбил первый предмет из сета Майкла Джексона", icon: "🕺", check: s => countMjEquippedOrOwned(s) >= 1 },
  { id: "a_mj_3", title: "Билли Джин на районе", desc: "Собрал 3 предмета из сета Майкла Джексона", icon: "🎩", check: s => countMjEquippedOrOwned(s) >= 3 },
  { id: "a_mj_6", title: "КОРОЛЬ ПОП-МУЗЫКИ (ФУЛЛ MJ)", desc: "Превратил манекена в Майкла Джексона (6/6 вещей)", icon: "👑", check: s => countMjEquipped(s) >= 6 },
  { id: "a_daily_spin", title: "Утренний Занос", desc: "Прокрутил бесплатную Ежедневную рулетку", icon: "☀️", check: s => s.stats.dailySpins >= 1 },
  { id: "a_weekly_spin", title: "Воскресный Бонус", desc: "Прокрутил Еженедельную рулетку", icon: "🎡", check: s => s.stats.weeklySpins >= 1 },
  { id: "a_mythic_drop", title: "Свидетель 0.15%", desc: "Выбил мифический предмет из рулетки", icon: "💎", check: s => s.inventory.includes("mythic_daily_glove") || s.inventory.includes("mythic_weekly_throne") },
  { id: "a_opush", title: "Опущенный Хаты", desc: "Уронил свою Ауру ниже нуля", icon: "🐓", check: s => s.aura < 0 }
];

[1, 3, 5, 10, 20, 35, 50, 75, 100, 150].forEach((n, i) => ACHIEVEMENTS_DB.push({ id: `ach_case_${n}`, title: `Лудоман Ур.${i+1}`, desc: `Открыть ${n} кейсов`, icon: "📦", check: s => s.stats.casesOpened >= n }));
[1, 3, 5, 10, 20, 35, 50, 75, 100].forEach((n, i) => ACHIEVEMENTS_DB.push({ id: `ach_upg_${n}`, title: `Крафтер Ур.${i+1}`, desc: `Успешно апгрейднуть ${n} раз`, icon: "⚡", check: s => s.stats.upgWins >= n }));

const PRESET_TASKS = [
  { title: "Вынес мусор и пустые бутылки 🗑️", hc: 1.5, aura: 8 },
  { title: "Помыл всю посуду и раковину 🍽️", hc: 2.0, aura: 10 },
  { title: "Приготовил похавать на всех (Омлет) 🍳", hc: 3.0, aura: 15 },
  { title: "Пропылесосил и помыл полы в хате 🧹", hc: 3.5, aura: 18 },
  { title: "Надраил толчок, ванну и плиту 🚽", hc: 4.5, aura: 22 },
  { title: "Забашлял за бухло / энергетики 🦌🥃", hc: 5.0, aura: 25 }
];

let state = {
  registered: false,
  nickname: "Бродяга",
  role: "Саня Жиросан 🐗",
  hc: 5.0,
  aura: 10,
  inventory: ["ptitsa_trusy", "kirill_shirt"],
  equipped: { head: null, face: null, body: "kirill_shirt", legs: "ptitsa_trusy", feet: null, acc: null },
  stats: { casesOpened: 0, upgWins: 0, upgFails: 0, tasksSent: 0, dailySpins: 0, weeklySpins: 0 },
  lastDailySpin: 0,
  lastWeeklySpin: 0,
  usedCodes: [],
  unlockedAch: [],
  sharedExpenses: [{ payer: "Саня", title: "Стартовая закупка продуктов", amount: 900 }]
};

let currentInvFilter = "all";

function loadState() {
  const raw = localStorage.getItem("trep_hata_v35_ultimate");
  if (raw) {
    try { state = Object.assign(state, JSON.parse(raw)); } catch (e) {}
  }
  if (!state.registered) {
    openRegistrationModal();
  }
  checkAllAchievements();
  refreshUI();
  setInterval(updateRouletteTimers, 1000);
}

function saveState() {
  localStorage.setItem("trep_hata_v35_ultimate", JSON.stringify(state));
}

function getAuraModifiers() {
  if (state.aura < 0) {
    return {
      title: state.aura <= -30 ? "🚽 Главный Опущенный Хаты" : "🐓 Опущенный (Аура в минусе)",
      caseMult: 1.25,
      upgBonus: -5,
      text: "ДЕБАФФ: Кейсы +25% дороже • Апгрейд -5%"
    };
  }
  const disc = Math.min(20, Math.floor(state.aura / 10));
  const upgB = Math.min(8, Math.floor(state.aura / 20));
  let title = "😐 Серый Пассажир";
  if (state.aura >= 150) title = "⚡ Святой Апостол Алхана";
  else if (state.aura >= 80) title = "👑 Смотрящий за Треп Хатой";
  else if (state.aura >= 40) title = "🔥 Уважаемый Кент";
  else if (state.aura >= 15) title = "🤝 Ровный Пацан";

  return {
    title,
    caseMult: (100 - disc) / 100,
    upgBonus: upgB,
    text: `Бафф Ауры: Скидка на кейсы -${disc}% • Апгрейд +${upgB}%`
  };
}

function getHcRankTitle() {
  if (state.aura < 0) return "🐓 Опущенный";
  if (state.hc < 0) return "💩 Ебучий лох (Должник)";
  if (state.hc < 10) return "🤡 Дух Треп Хаты";
  if (state.hc < 25) return "🧹 Младший по тарелочкам";
  if (state.hc < 60) return "🍺 Барон Холодильника";
  return "👑 Император Треп Хаты";
}

// РЕГИСТРАЦИЯ
let tempRegRole = "Саня Жиросан 🐗";
function openRegistrationModal() {
  const modal = document.getElementById("modal-onboard");
  const box = document.getElementById("onboard-box");
  modal.classList.add("open");
  const tgName = tg && tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user.first_name : "";

  box.innerHTML = `
    <h2 style="margin:0 0 6px; color:var(--gold);">🏠 РЕГИСТРАЦИЯ В ТРЕП ХАТЕ</h2>
    <p style="font-size:12px; color:var(--muted); margin:0 0 10px;">Стартовый баланс: <b>5.0 HC</b>!</p>
    <input type="text" id="reg-nick" class="inp" placeholder="Твой ник" value="${tgName}">
    <div style="display:grid; gap:6px; text-align:left; margin:8px 0;">
      <div class="task-row" style="margin:0; cursor:pointer; border-color:var(--gold);" onclick="pickRegRole('Саня Жиросан 🐗', this)">
        <div><b>🐗 Саня Жиросан</b><br><span style="font-size:10px; color:var(--muted);">Кодер, фанат Ягеря</span></div>
      </div>
      <div class="task-row" style="margin:0; cursor:pointer;" onclick="pickRegRole('Карась 🐟', this)">
        <div><b>🐟 Карась</b><br><span style="font-size:10px; color:var(--muted);">Шеф омлета</span></div>
      </div>
      <div class="task-row" style="margin:0; cursor:pointer;" onclick="pickRegRole('Карлик Джексон 🕺', this)">
        <div><b>🕺 Кирилл Умный</b><br><span style="font-size:10px; color:var(--muted);">Фанат MJ и бухгалтерии</span></div>
      </div>
    </div>
    <button class="btn-main gold" onclick="finishRegistration()">🚀 ВОРВАТЬСЯ</button>
  `;
}
function pickRegRole(r, el) {
  tempRegRole = r;
  el.parentElement.querySelectorAll(".task-row").forEach(x => x.style.borderColor = "#263147");
  el.style.borderColor = "#f59e0b";
  playSound("click");
}
function finishRegistration() {
  const val = document.getElementById("reg-nick").value.trim();
  state.nickname = val || tempRegRole.split(" ")[0];
  state.role = tempRegRole;
  state.hc = 5.0;
  state.registered = true;
  saveState();
  playSound("win");
  document.getElementById("modal-onboard").classList.remove("open");
  refreshUI();
}

// МАНЕКЕН И ИНВЕНТАРЬ
function countMjEquipped(s) {
  const mjIds = ["mj_hat", "mj_glasses", "mj_jacket", "mj_pants", "mj_shoes", "mj_glove"];
  return Object.values(s.equipped).filter(id => mjIds.includes(id)).length;
}
function countMjEquippedOrOwned(s) {
  const mjIds = ["mj_hat", "mj_glasses", "mj_jacket", "mj_pants", "mj_shoes", "mj_glove"];
  return mjIds.filter(id => s.inventory.includes(id) || Object.values(s.equipped).includes(id)).length;
}

function renderMannequin() {
  const slots = ["head", "face", "body", "legs", "feet", "acc"];
  document.getElementById("layer-back").innerHTML = "";

  slots.forEach(sl => {
    const layer = document.getElementById(`layer-${sl}`);
    const cell = document.getElementById(`slot-cell-${sl}`);
    const valTxt = document.getElementById(`slot-val-${sl}`);
    const itemId = state.equipped[sl];

    if (itemId && ITEMS_DB[itemId]) {
      const it = ITEMS_DB[itemId];
      if (it.isBackLayer) {
        document.getElementById("layer-back").innerHTML += it.mannequinSvg;
        layer.innerHTML = "";
      } else {
        layer.innerHTML = it.mannequinSvg;
      }
      cell.classList.add("filled");
      valTxt.innerText = it.name;
    } else {
      layer.innerHTML = "";
      cell.classList.remove("filled");
      valTxt.innerText = "Пусто";
    }
  });

  const mjCount = countMjEquipped(state);
  document.getElementById("mj-progress-badge").innerText = mjCount === 6 ? "👑 ФУЛЛ МАЙКЛ ДЖЕКСОН!" : `🕺 Сет MJ: ${mjCount}/6`;

  const opushLayer = document.getElementById("layer-opush");
  const stageCard = document.getElementById("mannequin-stage-card");
  if (state.aura < 0) {
    stageCard.classList.add("opush-stage");
    opushLayer.innerHTML = `<rect x="52" y="138" width="96" height="22" rx="5" fill="#ef4444" stroke="#fff" stroke-width="1.5"/><text x="100" y="153" font-size="10" text-anchor="middle" fill="#fff" font-weight="900">🐓 ОПУЩЕННЫЙ</text>`;
  } else {
    stageCard.classList.remove("opush-stage");
    opushLayer.innerHTML = "";
  }
}

function equipItem(id) {
  const it = ITEMS_DB[id];
  if (!it || it.slot === "coins") return;
  state.equipped[it.slot] = id;
  playSound("click");
  saveState();
  refreshUI();
}

function unequipSlot(slot) {
  if (!state.equipped[slot]) return;
  state.equipped[slot] = null;
  playSound("click");
  saveState();
  refreshUI();
}

function sellInventoryItem(idx) {
  const itemId = state.inventory[idx];
  const it = ITEMS_DB[itemId];
  if (!it) return;
  state.inventory.splice(idx, 1);
  if (state.equipped[it.slot] === itemId && !state.inventory.includes(itemId)) {
    state.equipped[it.slot] = null;
  }
  state.hc = Math.round((state.hc + it.price) * 10) / 10;
  playSound("win");
  saveState();
  refreshUI();
}

function sellAllDuplicates() {
  const seen = new Set();
  const kept = [];
  let earned = 0;
  state.inventory.forEach(id => {
    const it = ITEMS_DB[id];
    // Можем продавать только дубликаты шмоток (не монеты)
    if (it.slot !== "coins" && seen.has(id)) {
      earned += it.price;
      // Если вещь была надета и в инвентаре больше нет копий, снимаем
      if (state.equipped[it.slot] === id) state.equipped[it.slot] = null;
    } else {
      seen.add(id);
      kept.push(id);
    }
  });
  state.inventory = kept;
  state.hc = Math.round((state.hc + earned) * 10) / 10;
  playSound("win");
  saveState();
  refreshUI();
  alert(`Продано дубликатов на +${earned.toFixed(1)} HC!`);
}

function filterInventory(slot, btn) {
  currentInvFilter = slot;
  document.querySelectorAll(".filter-chip").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  renderInventoryGrid();
}

function renderInventoryGrid() {
  const box = document.getElementById("inv-grid-box");
  document.getElementById("inv-counter").innerText = state.inventory.length;

  const list = state.inventory
    .map((id, idx) => ({ id, idx, item: ITEMS_DB[id] }))
    .filter(x => x.item && (currentInvFilter === "all" || x.item.slot === currentInvFilter));

  if (list.length === 0) {
    box.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:20px; color:var(--muted); font-size:12px;">Инвентарь пуст.</div>`;
    return;
  }

  box.innerHTML = list.map(({ id, idx, item }) => {
    const worn = state.equipped[item.slot] === id;
    return `
      <div class="item-box r-${item.rarity}">
        <div>
          <div class="item-svg-wrap">${item.iconSvg}</div>
          <div class="item-title">${item.name}</div>
          <div class="item-info">${item.rarity.toUpperCase()} • ${item.price} HC</div>
        </div>
        <div class="item-btns">
          <button class="btn-mini btn-wear ${worn ? 'worn' : ''}" onclick="equipItem('${id}')">${worn ? "✅ Надет" : "👕 Надеть"}</button>
          <button class="btn-mini btn-sell" onclick="sellInventoryItem(${idx})">+${item.price}</button>
        </div>
      </div>
    `;
  }).join("");
}

// РУЛЕТКИ И ТАЙМЕРЫ
function updateRouletteTimers() {
  const now = Date.now();
  const dDiff = 24 * 3600 * 1000 - (now - state.lastDailySpin);
  const wDiff = 7 * 24 * 3600 * 1000 - (now - state.lastWeeklySpin);

  const dLbl = document.getElementById("daily-timer-lbl");
  const wLbl = document.getElementById("weekly-timer-lbl");
  const dBtn = document.getElementById("btn-daily-spin");
  const wBtn = document.getElementById("btn-weekly-spin");

  if (dDiff > 0) {
    const hrs = Math.floor(dDiff / 3600000);
    const mins = Math.floor((dDiff % 3600000) / 60000);
    dLbl.innerText = `Перезарядка: ${hrs}ч ${mins}м`;
    dBtn.disabled = true;
    dBtn.style.opacity = "0.5";
  } else {
    dLbl.innerText = "Доступно!";
    dBtn.disabled = false;
    dBtn.style.opacity = "1";
  }

  if (wDiff > 0) {
    const days = Math.floor(wDiff / (24 * 3600000));
    const hrs = Math.floor((wDiff % (24 * 3600000)) / 3600000);
    wLbl.innerText = `Перезарядка: ${days}д ${hrs}ч`;
    wBtn.disabled = true;
    wBtn.style.opacity = "0.5";
  } else {
    wLbl.innerText = "Доступно!";
    wBtn.disabled = false;
    wBtn.style.opacity = "1";
  }
}

// КЕЙСЫ
let activeSpinMode = null;
let isSpinningNow = false;

function renderCasesGrid() {
  const box = document.getElementById("cases-grid-box");
  box.innerHTML = CASES_DB.map(c => {
    const p = Math.max(1, Math.round(c.price * getAuraModifiers().caseMult * 10) / 10);
    return `
      <div class="case-box" onclick="openCasePreview('${c.id}')">
        <div class="case-icon"><svg viewBox="0 0 80 80"><rect x="12" y="20" width="56" height="46" rx="10" fill="#1e293b" stroke="${c.color}" stroke-width="3"/><circle cx="40" cy="43" r="11" fill="${c.color}"/></svg></div>
        <div style="font-weight:900; font-size:13px;">${c.name}</div>
        <div class="case-price-tag">${p} HC</div>
      </div>
    `;
  }).join("");
}

function openCasePreview(id) {
  const c = CASES_DB.find(x => x.id === id);
  if (!c) return;
  playSound("click");
  const p = Math.max(1, Math.round(c.price * getAuraModifiers().caseMult * 10) / 10);
  activeSpinMode = { type: "case", caseObj: c, cost: p, pool: c.items };
  document.getElementById("m-case-name").innerText = c.name;
  document.getElementById("m-case-sub").innerText = `Цена: ${p} HC`;
  document.getElementById("m-drop-msg").innerText = "";
  fillModalPreviewAndTrack(c.items);
  document.getElementById("modal-case").classList.add("open");
}

function openFreeRoulette(kind) {
  if (kind === "daily") {
    activeSpinMode = { type: "daily", cost: 0, pool: ["coins_1", "coins_3", "coins_7", "trusy_karasya", "mythic_daily_glove"], mythicId: "mythic_daily_glove" };
    document.getElementById("m-case-name").innerText = "☀️ Ежедневная рулетка";
  } else {
    activeSpinMode = { type: "weekly", cost: 0, pool: ["coins_3", "coins_7", "coins_15", "sanya_robe", "mythic_weekly_throne"], mythicId: "mythic_weekly_throne" };
    document.getElementById("m-case-name").innerText = "👑 Еженедельная рулетка";
  }
  document.getElementById("m-case-sub").innerText = "Бесплатно! Шанс 0.15% на мифик!";
  document.getElementById("m-drop-msg").innerText = "";
  fillModalPreviewAndTrack(activeSpinMode.pool);
  document.getElementById("modal-case").classList.add("open");
}

function fillModalPreviewAndTrack(pool) {
  document.getElementById("m-loot-grid").innerHTML = pool.map(id => {
    const it = ITEMS_DB[id];
    return `<div class="preview-cell">${it.iconSvg}<b>${it.name}</b><span style="color:var(--gold);">${it.price} HC</span></div>`;
  }).join("");

  const strip = document.getElementById("m-roller-strip");
  strip.style.transition = "none";
  strip.style.transform = "translateX(0px)";
  strip.innerHTML = pool.map(id => `<div class="r-item-card">${ITEMS_DB[id].iconSvg}<span>${ITEMS_DB[id].name}</span></div>`).join("");
}

function closeCaseModal() {
  if (isSpinningNow) return;
  document.getElementById("modal-case").classList.remove("open");
}

function executeModalSpin() {
  if (isSpinningNow || !activeSpinMode) return;

  if (activeSpinMode.type === "case") {
    if (state.hc < activeSpinMode.cost) {
      playSound("fail");
      alert("Не хватает ХатаКойнов!");
      return;
    }
    state.hc = Math.round((state.hc - activeSpinMode.cost) * 10) / 10;
  } else if (activeSpinMode.type === "daily") {
    state.lastDailySpin = Date.now();
    state.stats.dailySpins++;
  } else if (activeSpinMode.type === "weekly") {
    state.lastWeeklySpin = Date.now();
    state.stats.weeklySpins++;
  }

  isSpinningNow = true;
  document.getElementById("btn-spin-modal").disabled = true;
  document.getElementById("btn-close-modal").disabled = true;
  document.getElementById("m-drop-msg").innerText = "Крутим...";
  refreshUI();

  let winId;
  const pool = activeSpinMode.pool;
  if (activeSpinMode.mythicId && Math.random() * 100 <= 0.15) {
    winId = activeSpinMode.mythicId;
  } else {
    const filtered = activeSpinMode.mythicId ? pool.filter(x => x !== activeSpinMode.mythicId) : pool;
    winId = filtered[Math.floor(Math.random() * filtered.length)];
  }

  const winItem = ITEMS_DB[winId];
  const WIN_POS = 34;
  let html = "";
  for (let i = 0; i < 42; i++) {
    const id = i === WIN_POS ? winId : pool[Math.floor(Math.random() * pool.length)];
    html += `<div class="r-item-card">${ITEMS_DB[id].iconSvg}<span>${ITEMS_DB[id].name}</span></div>`;
  }

  const strip = document.getElementById("m-roller-strip");
  strip.style.transition = "none";
  strip.style.transform = "translateX(0px)";
  strip.innerHTML = html;

  const offset = (WIN_POS * 96) - (document.querySelector(".roller-window").clientWidth / 2) + 48;
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      strip.style.transition = "transform 3.5s cubic-bezier(0.08, 0.85, 0.14, 1)";
      strip.style.transform = `translateX(-${offset}px)`;
    });
  });

  [300, 700, 1200, 1800, 2500, 3100].forEach(ms => setTimeout(() => playSound("tick"), ms));

  setTimeout(() => {
    if (winItem.slot === "coins") {
      state.hc = Math.round((state.hc + winItem.price) * 10) / 10;
      document.getElementById("m-drop-msg").innerText = `💰 ВЫПАЛИ КОЙНЫ: ${winItem.name}!`;
    } else {
      state.inventory.push(winId);
      document.getElementById("m-drop-msg").innerText = `🎉 ВЫПАЛ ПРЕДМЕТ: ${winItem.name}!`;
    }
    if (activeSpinMode.type === "case") state.stats.casesOpened++;

    playSound("win");
    checkAllAchievements();
    saveState();
    refreshUI();

    document.getElementById("btn-spin-modal").disabled = false;
    document.getElementById("btn-close-modal").disabled = false;
    isSpinningNow = false;
  }, 3600);
}

// АПГРЕЙД
let upgBaseChance = 50;
let upgAngle = 0;
let isUpgRunning = false;

function selectUpgChance(pct, btn) {
  if (isUpgRunning) return;
  upgBaseChance = pct;
  document.querySelectorAll(".ch-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  playSound("click");
  updateUpgradePreview();
}

function renderUpgradeSelect() {
  const sel = document.getElementById("upg-item-select");
  if (state.inventory.length === 0) {
    sel.innerHTML = `<option value="">Инвентарь пуст</option>`;
    document.getElementById("upg-left-slot").innerHTML = "Пусто";
    document.getElementById("upg-right-slot").innerHTML = "—";
    return;
  }
  sel.innerHTML = state.inventory.map((id, i) => `<option value="${i}">${ITEMS_DB[id].name} (${ITEMS_DB[id].price} HC)</option>`).join("");
  updateUpgradePreview();
}

function updateUpgradePreview() {
  const eff = Math.max(2, Math.min(92, upgBaseChance + getAuraModifiers().upgBonus));
  document.getElementById("upg-pct-text").innerText = `${eff}%`;
  document.getElementById("upg-circle").style.background = `conic-gradient(var(--green) 0% ${eff}%, #1e293b ${eff}% 100%)`;

  const sel = document.getElementById("upg-item-select");
  const idx = parseInt(sel.value, 10);
  if (isNaN(idx) || !state.inventory[idx]) return;

  const src = ITEMS_DB[state.inventory[idx]];
  const mult = upgBaseChance === 10 ? 5.0 : upgBaseChance === 30 ? 2.5 : upgBaseChance === 50 ? 1.8 : 1.3;
  const target = WEARABLE_SORTED.filter(x => x.price > src.price)[0] || WEARABLE_SORTED[WEARABLE_SORTED.length - 1];

  document.getElementById("upg-left-slot").innerHTML = `${src.iconSvg}<b>${src.name}</b>`;
  document.getElementById("upg-right-slot").innerHTML = `${target.iconSvg}<b style="color:var(--gold);">${target.name}</b>`;
}

function runUpgradeWheel() {
  if (isUpgRunning) return;
  const sel = document.getElementById("upg-item-select");
  const idx = parseInt(sel.value, 10);
  if (isNaN(idx) || !state.inventory[idx]) {
    alert("Выбери шмотку!");
    return;
  }

  isUpgRunning = true;
  document.getElementById("btn-do-upgrade").disabled = true;

  const srcId = state.inventory[idx];
  const srcItem = ITEMS_DB[srcId];
  const target = WEARABLE_SORTED.filter(x => x.price > srcItem.price)[0] || WEARABLE_SORTED[WEARABLE_SORTED.length - 1];
  const eff = Math.max(2, Math.min(92, upgBaseChance + getAuraModifiers().upgBonus));

  const win = Math.random() * 100 <= eff;
  const stopDeg = win ? Math.random() * (eff * 3.6 - 8) + 4 : (eff * 3.6) + 10 + Math.random() * 50;

  upgAngle += (360 * 5) + stopDeg;
  document.getElementById("upg-arrow").style.transform = `translateX(-50%) rotate(${upgAngle}deg)`;

  [300, 800, 1400, 2200].forEach(ms => setTimeout(() => playSound("tick"), ms));

  setTimeout(() => {
    state.inventory.splice(idx, 1);
    if (state.equipped[srcItem.slot] === srcId && !state.inventory.includes(srcId)) {
      state.equipped[srcItem.slot] = null;
    }

    if (win) {
      state.inventory.push(target.id);
      state.stats.upgWins++;
      playSound("win");
      document.getElementById("upg-sub-status").innerHTML = `<b style="color:var(--green);">УСПЕХ! +${target.name}</b>`;
    } else {
      state.stats.upgFails++;
      playSound("fail");
      document.getElementById("upg-sub-status").innerHTML = `<b style="color:var(--red);">СКАМ! Сгорело!</b>`;
    }

    checkAllAchievements();
    saveState();
    refreshUI();
    document.getElementById("btn-do-upgrade").disabled = false;
    isUpgRunning = false;
  }, 3300);
}

// ЗАДАНИЯ И ПИН-КОДЫ (УМНЫЙ ДЕКОДЕР КРИПТО-КОДОВ)
function calcCustomReward(text) {
  const t = (text || "").toLowerCase();
  let hc = 1.5, aura = 8;
  ["ягер", "виск", "алко", "пив", "купил", "забашлял", "толчок", "унитаз", "плит", "омлет"].forEach(w => { if (t.includes(w)) { hc += 1.2; aura += 6; } });
  ["мусор", "посуд", "приготов", "убрал", "помыл", "магаз"].forEach(w => { if (t.includes(w)) { hc += 0.7; aura += 4; } });
  return { hc: Math.round(Math.min(5.0, Math.max(1.0, hc)) * 2) / 2, aura: Math.min(30, Math.max(5, aura)) };
}

function liveEstimateCustomTask() {
  const est = calcCustomReward(document.getElementById("custom-task-inp").value);
  document.getElementById("custom-task-est").innerText = `+${est.hc} HC и +${est.aura} Ауры`;
}

function sendCustomTaskToChats() {
  const txt = document.getElementById("custom-task-inp").value.trim();
  if (txt.length < 3) { alert("Опиши задачу подробнее!"); return; }
  const est = calcCustomReward(txt);
  state.stats.tasksSent++;
  saveState();

  if (tg && tg.sendData) {
    tg.sendData(JSON.stringify({ action: "create_task_poll", title: txt, reward: est.hc, aura: est.aura }));
  } else {
    alert(`Заявка отправлена в чат! После 2 голосов пацанов придёт Пин-код на +${est.hc} HC.`);
  }
  document.getElementById("custom-task-inp").value = "";
}

function renderPresetTasks() {
  document.getElementById("preset-tasks-box").innerHTML = PRESET_TASKS.map(t => `
    <div class="task-row">
      <div>
        <div style="font-weight:800; font-size:13px;">${t.title}</div>
        <div style="font-size:11px; color:var(--muted);">Награда: <b style="color:var(--gold);">+${t.hc} HC</b> и <b>+${t.aura} ✨</b></div>
      </div>
      <button class="task-btn" onclick="sendPresetTask('${t.title}', ${t.hc}, ${t.aura})">📢 В чат</button>
    </div>
  `).join("");
}

function sendPresetTask(title, hc, aura) {
  state.stats.tasksSent++;
  saveState();
  if (tg && tg.sendData) {
    tg.sendData(JSON.stringify({ action: "create_task_poll", title, reward: hc, aura }));
  } else {
    alert(`Заявка «${title}» отправлена в чат! Жди 2 голоса пацанов.`);
  }
}

function redeemClaimCode() {
  const code = document.getElementById("claim-code-inp").value.trim().toUpperCase();
  if (!code.startsWith("HATA-")) {
    playSound("fail");
    alert("Неверный формат Пин-кода!");
    return;
  }
  if (state.usedCodes.includes(code)) {
    playSound("fail");
    alert("Этот Пин-код уже активирован!");
    return;
  }

  // УМНЫЙ ДЕКОДЕР: формат HATA-HC-AURA-SALT-CHECK
  const parts = code.split("-");
  if (parts.length < 5) {
    playSound("fail");
    alert("Ошибка кода!");
    return;
  }

  const hcVal = parseInt(parts[1], 10) / 10;
  const auraVal = parseInt(parts[2], 10);

  if (isNaN(hcVal) || isNaN(auraVal)) {
    playSound("fail");
    alert("Повреждённый код!");
    return;
  }

  state.usedCodes.push(code);
  state.hc = Math.round((state.hc + hcVal) * 10) / 10;
  state.aura += auraVal;
  document.getElementById("claim-code-inp").value = "";
  playSound("win");
  checkAllAchievements();
  saveState();
  refreshUI();
  alert(`✅ Код активирован! Зачислено +${hcVal} HC и +${auraVal} Ауры!`);
}

// БУХГАЛТЕРИЯ
function addSharedExpense() {
  const title = document.getElementById("exp-title-inp").value.trim();
  const amount = parseFloat(document.getElementById("exp-amount-inp").value);
  const payer = document.getElementById("exp-payer-inp").value;

  if (!title || isNaN(amount) || amount <= 0) {
    alert("Заполни название и сумму!");
    return;
  }
  state.sharedExpenses.unshift({ payer, title, amount });
  document.getElementById("exp-title-inp").value = "";
  document.getElementById("exp-amount-inp").value = "";
  playSound("win");
  saveState();
  renderSharedExpenses();

  if (tg && tg.sendData) {
    tg.sendData(JSON.stringify({ action: "add_expense", payer, title, amount }));
  }
}

function renderSharedExpenses() {
  const box = document.getElementById("expenses-summary-box");
  const totals = { "Саня": 0, "Карась": 0, "Кирилл": 0 };
  let sumAll = 0;
  state.sharedExpenses.forEach(e => {
    totals[e.payer] = (totals[e.payer] || 0) + e.amount;
    sumAll += e.amount;
  });

  box.innerHTML = `
    <div style="background:#090d16; padding:8px; border-radius:10px; margin-bottom:8px;">
      <div>Всего потрачено: <b>${sumAll} ₽</b> (Доля каждого: <b>${Math.round(sumAll/3)} ₽</b>)</div>
      <div style="margin-top:4px; color:#cbd5e1;">Саня: ${totals["Саня"]} ₽ | Карась: ${totals["Карась"]} ₽ | Кирилл: ${totals["Кирилл"]} ₽</div>
    </div>
    ${state.sharedExpenses.slice(0, 4).map(e => `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #1e293b;"><span><b>${e.payer}:</b>${e.title}</span><b style="color:var(--gold);">${e.amount} ₽</b></div>`).join("")}
  `;
}

function renderLeaderboardAndAchievements() {
  const lb = document.getElementById("leaderboard-box");
  const players = [
    { name: state.nickname, role: state.role, hc: state.hc, aura: state.aura, isMe: true },
    { name: "Карась", role: "Охотник на самок 🐟", hc: 14.5, aura: 25, isMe: false },
    { name: "Кирилл Умный", role: "Карлик Джексон 🕺", hc: 19.0, aura: 40, isMe: false }
  ].sort((a, b) => b.hc - a.hc);

  lb.innerHTML = players.map((p, i) => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px solid #1e293b; ${p.isMe ? 'background:rgba(245,158,11,0.1);border-radius:10px;' : ''}">
      <div><b>#${i+1} ${p.name}</b> <span style="font-size:10px;color:var(--muted);">(${p.role})</span><br><span style="font-size:11px;color:${p.aura<0?'var(--red)':'#c4b5fd'};">${p.aura<0?'🐓 Опущенный':`✨ Аура: ${p.aura}`}</span></div>
      <div style="font-weight:900; color:var(--gold);">${p.hc.toFixed(1)} HC</div>
    </div>
  `).join("");

  document.getElementById("ach-progress-txt").innerText = `${state.unlockedAch.length}/${ACHIEVEMENTS_DB.length}`;
  document.getElementById("achievements-list-box").innerHTML = ACHIEVEMENTS_DB.map(a => {
    const done = state.unlockedAch.includes(a.id);
    return `<div class="ach-item ${done ? 'done' : ''}"><div style="font-size:22px;">${a.icon}</div><div><div style="font-weight:900; font-size:12px;">${a.title} ${done ? '✅' : '🔒'}</div><div style="font-size:11px; color:var(--muted);">${a.desc}</div></div></div>`;
  }).join("");
}

function checkAllAchievements() {
  ACHIEVEMENTS_DB.forEach(a => {
    if (!state.unlockedAch.includes(a.id) && a.check(state)) {
      state.unlockedAch.push(a.id);
    }
  });
}

function syncProfileToBot() {
  playSound("click");
  if (tg && tg.sendData) {
    tg.sendData(JSON.stringify({
      action: "sync_profile",
      nickname: state.nickname,
      role: state.role,
      hc: state.hc,
      aura: state.aura,
      cases_opened: state.stats.casesOpened,
      inv_count: state.inventory.length,
      outfit: {
        head: state.equipped.head ? ITEMS_DB[state.equipped.head].name : "Нет",
        face: state.equipped.face ? ITEMS_DB[state.equipped.face].name : "Нет",
        body: state.equipped.body ? ITEMS_DB[state.equipped.body].name : "Нет",
        legs: state.equipped.legs ? ITEMS_DB[state.equipped.legs].name : "Нет",
        feet: state.equipped.feet ? ITEMS_DB[state.equipped.feet].name : "Нет",
        acc: state.equipped.acc ? ITEMS_DB[state.equipped.acc].name : "Нет"
      }
    }));
    alert("Профиль выгружен в чат Telegram!");
  } else {
    alert("Открой Mini App через бота в Telegram!");
  }
}

function openTab(pageId, btn) {
  document.querySelectorAll(".tab-page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(`page-${pageId}`).classList.add("active");
  if (btn) btn.classList.add("active");
  playSound("click");
}

function refreshUI() {
  document.getElementById("hdr-nick").innerText = state.nickname;
  document.getElementById("hdr-role").innerText = state.role;
  document.getElementById("hdr-hc").innerText = state.hc.toFixed(1);
  document.getElementById("hdr-aura").innerText = state.aura;
  document.getElementById("hdr-hc-rank").innerText = getHcRankTitle();

  const mod = getAuraModifiers();
  const auraRankEl = document.getElementById("hdr-aura-rank");
  auraRankEl.innerText = mod.title;
  auraRankEl.className = state.aura < 0 ? "aura-line opush" : "aura-line";

  document.getElementById("pill-hc").className = state.hc < 0 ? "bal-pill bal-hc debt" : "bal-pill bal-hc";
  document.getElementById("pill-aura").className = state.aura < 0 ? "bal-pill bal-aura opush" : "bal-pill bal-aura";
  document.getElementById("aura-buff-text").innerText = mod.text;

  renderMannequin();
  renderInventoryGrid();
  renderCasesGrid();
  renderUpgradeSelect();
  renderPresetTasks();
  renderSharedExpenses();
  renderLeaderboardAndAchievements();
}

loadState();