let tg = window.Telegram.WebApp;
tg.expand();

let userHC = 45.0;
let inventory = [
    { name: "Выцветшая майка Карася", type: "body", price: 0.1 },
    { name: "Проссанные тапки Кирилла", type: "acc", price: 0.2 }
];

function updateUI() {
    document.getElementById('hc-balance').innerText = userHC.toFixed(1);
    renderInventory();
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Список возможного дропа из кейсов (без кринжа, только лор и шмот)
const lootPool = [
    { name: "Трусы Карася в горошек", type: "body", price: 0.1, rarity: "обычный" },
    { name: "Очки слепого пса", type: "acc", price: 0.5, rarity: "редкий" },
    { name: "Шлем ебучего султана", type: "head", price: 10.0, rarity: "легендарный" },
    { name: "Носки алхана", type: "acc", price: 0.2, rarity: "обычный" },
    { name: "Золотая цепь карлика Джексона", type: "acc", price: 10.0, rarity: "легендарный" }
];

function openCase(cost) {
    if (userHC < cost) {
        alert("Не хватает ХатаКойнов, иди мой посуду или убирайся!");
        return;
    }
    userHC -= cost;
    
    // Рандомный дроп
    let item = lootPool[Math.floor(Math.random() * lootPool.length)];
    inventory.push(item);
    
    updateUI();
    alert(`🎉 Из кейса выпало: ${item.name} (${item.rarity.toUpperCase()})!`);
}

function tryUpgrade(chance) {
    if (inventory.length === 0) {
        alert("У тебя нет шмоток для апгрейда!");
        return;
    }
    
    let success = Math.random() * 100 < chance;
    if (success) {
        alert(`🔥 УСПЕХ (${chance}%)! Твоя шмотка апгрейднулась в мега-легендарку!`);
    } else {
        inventory.shift(); // Сгорает шмотка
        alert(`💥 СКАМ (${chance}%)! Шмотка сгорела нахуй в печи.`);
    }
    updateUI();
}

function renderInventory() {
    let list = document.getElementById('inventory-list');
    list.innerHTML = "";
    inventory.forEach((item, index) => {
        list.innerHTML += `
            <div class="slot">
                <strong>${item.name}</strong><br>
                Цена: ${item.price} HC<br>
                <button onclick="sellItem(${index})" style="background:#c0392b; color:#fff; border:none; padding:3px 6px; border-radius:4px; margin-top:4px;">Продать (${item.price} HC)</button>
            </div>
        `;
    });
}

function sellItem(index) {
    let sold = inventory.splice(index, 1)[0];
    userHC += sold.price;
    updateUI();
}

updateUI();