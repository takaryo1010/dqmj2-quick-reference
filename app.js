// DQMJ2 モンスター情報比較ツール - JavaScript版
// GitHub Pages対応

let monstersData = {};
let selectedMonsters = ['', '', ''];
let resistanceLevels = ['通常', '通常', '通常'];
let dropdownStates = [false, false, false]; // ドロップダウンの開閉状態
let autocompleteStates = [{}, {}, {}]; // 各入力フィールドのオートコンプリート状態

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    loadMonsterData();
    setupEventListeners();
});

// モンスターデータの読み込み
async function loadMonsterData() {
    try {
        const response = await fetch('dqmj2_monsters.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        monstersData = await response.json();
        
        console.log('モンスターデータ読み込み完了:', Object.keys(monstersData).length, '体');
        
        updateStats();
        hideLoading();
        
    } catch (error) {
        console.error('データ読み込みエラー:', error);
        showError();
    }
}

// イベントリスナーの設定
function setupEventListeners() {
    for (let i = 1; i <= 3; i++) {
        // モンスター入力（テキスト入力）
        const input = document.getElementById(`monster${i}-input`);
        input.addEventListener('input', function() {
            handleAutocomplete(i, this.value);
        });
        
        input.addEventListener('focus', function() {
            if (this.value === '') {
                showAllMonsters(i);
            }
        });
        
        input.addEventListener('keydown', function(e) {
            handleKeyNavigation(i, e);
        });
        
        input.addEventListener('blur', function() {
            // 少し遅延させてクリックイベントを処理できるようにする
            setTimeout(() => hideAutocomplete(i), 200);
        });
        
        // 耐性レベル選択
        const radios = document.querySelectorAll(`input[name="resistance_level_${i}"]`);
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                resistanceLevels[i-1] = this.value;
                updateDisplay();
            });
        });
    }
    
    // 外部クリックでドロップダウンを閉じる
    document.addEventListener('click', function(e) {
        for (let i = 1; i <= 3; i++) {
            const combo = document.getElementById(`monster${i}-combo`);
            if (!combo.contains(e.target)) {
                closeDropdown(i);
            }
        }
    });
}

// ドロップダウンの切り替え
function toggleDropdown(index) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    const combo = document.getElementById(`monster${index}-combo`);
    
    if (dropdownStates[index-1]) {
        closeDropdown(index);
    } else {
        // 他のドロップダウンを閉じる
        for (let i = 1; i <= 3; i++) {
            if (i !== index) {
                closeDropdown(i);
            }
        }
        
        // 現在のドロップダウンを開く
        showAllMonsters(index);
        combo.classList.add('open');
        dropdownStates[index-1] = true;
    }
}

// ドロップダウンを閉じる
function closeDropdown(index) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    const combo = document.getElementById(`monster${index}-combo`);
    
    autocompleteDiv.style.display = 'none';
    combo.classList.remove('open');
    dropdownStates[index-1] = false;
}

// 全モンスターを表示
function showAllMonsters(index) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    const monsterNames = Object.keys(monstersData).sort();
    
    autocompleteDiv.innerHTML = '';
    monsterNames.slice(0, 20).forEach((name, i) => { // 最初の20件を表示
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        if (i === 0) item.classList.add('selected');
        
        const system = monstersData[name].系統 || '未知';
        item.innerHTML = `
            <span class="monster-name">${name}</span>
            <span class="monster-type">[${system}]</span>
        `;
        item.dataset.value = name;
        
        item.addEventListener('click', function() {
            selectMonster(index, name);
        });
        
        autocompleteDiv.appendChild(item);
    });
    
    autocompleteDiv.style.display = 'block';
    autocompleteStates[index-1] = { matches: monsterNames.slice(0, 20), selectedIndex: 0 };
}

// オートコンプリート処理
function handleAutocomplete(index, query) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    
    if (!query.trim()) {
        hideAutocomplete(index);
        selectedMonsters[index-1] = '';
        toggleResistanceLevel(index, false);
        updateDisplay();
        return;
    }
    
    // モンスター名を検索（部分一致、ひらがな/カタカナ対応）
    const normalizedQuery = normalizeString(query.toLowerCase());
    const matches = Object.keys(monstersData).filter(name => {
        const normalizedName = normalizeString(name.toLowerCase());
        const system = monstersData[name].系統 || '';
        
        // 名前の部分一致、系統の部分一致、読み方の部分一致
        return normalizedName.includes(normalizedQuery) ||
               name.toLowerCase().includes(query.toLowerCase()) ||
               system.includes(query) ||
               // 前方一致も重視
               normalizedName.startsWith(normalizedQuery) ||
               name.toLowerCase().startsWith(query.toLowerCase());
    });
    
    // 関連度でソート（前方一致を優先）
    matches.sort((a, b) => {
        const normalizedA = normalizeString(a.toLowerCase());
        const normalizedB = normalizeString(b.toLowerCase());
        const queryLower = query.toLowerCase();
        const normalizedQueryLower = normalizeString(queryLower);
        
        // 完全一致
        if (normalizedA === normalizedQueryLower) return -1;
        if (normalizedB === normalizedQueryLower) return 1;
        if (a.toLowerCase() === queryLower) return -1;
        if (b.toLowerCase() === queryLower) return 1;
        
        // 前方一致
        const aStartsNormalized = normalizedA.startsWith(normalizedQueryLower);
        const bStartsNormalized = normalizedB.startsWith(normalizedQueryLower);
        const aStartsOriginal = a.toLowerCase().startsWith(queryLower);
        const bStartsOriginal = b.toLowerCase().startsWith(queryLower);
        
        if (aStartsNormalized && !bStartsNormalized) return -1;
        if (!aStartsNormalized && bStartsNormalized) return 1;
        if (aStartsOriginal && !bStartsOriginal) return -1;
        if (!aStartsOriginal && bStartsOriginal) return 1;
        
        // 文字列長で並び替え（短い方を優先）
        return a.length - b.length;
    }).slice(0, 8); // 最大8件
    
    if (matches.length === 0) {
        hideAutocomplete(index);
        return;
    }
    
    // オートコンプリートリストを表示
    autocompleteDiv.innerHTML = '';
    matches.forEach((name, i) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        if (i === 0) item.classList.add('selected'); // 最初の項目を選択状態に
        
        const system = monstersData[name].系統 || '未知';
        // ハイライト表示
        const highlightedName = highlightMatch(name, query);
        item.innerHTML = `
            <span class="monster-name">${highlightedName}</span>
            <span class="monster-type">[${system}]</span>
        `;
        item.dataset.value = name;
        
        item.addEventListener('click', function() {
            selectMonster(index, name);
        });
        
        autocompleteDiv.appendChild(item);
    });
    
    autocompleteDiv.style.display = 'block';
    const combo = document.getElementById(`monster${index}-combo`);
    combo.classList.add('open');
    dropdownStates[index-1] = true;
    autocompleteStates[index-1] = { matches, selectedIndex: 0 };
}

// 文字列正規化（ひらがな⇔カタカナ変換）
function normalizeString(str) {
    return str
        // ひらがなをカタカナに変換
        .replace(/[\u3041-\u3096]/g, function(match) {
            const chr = match.charCodeAt(0) + 0x60;
            return String.fromCharCode(chr);
        })
        // 全角英数字を半角に変換
        .replace(/[Ａ-Ｚａ-ｚ０-９]/g, function(s) {
            return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);
        });
}

// マッチした部分をハイライト
function highlightMatch(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    return text.replace(regex, '<span style="background-color: yellow; color: black;">$1</span>');
}

// 正規表現エスケープ
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// キーボードナビゲーション
function handleKeyNavigation(index, e) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    const state = autocompleteStates[index-1];
    
    if (!state.matches || state.matches.length === 0) return;
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            state.selectedIndex = Math.min(state.selectedIndex + 1, state.matches.length - 1);
            updateSelectedItem(index);
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            state.selectedIndex = Math.max(state.selectedIndex - 1, 0);
            updateSelectedItem(index);
            break;
            
        case 'Enter':
            e.preventDefault();
            if (state.matches[state.selectedIndex]) {
                selectMonster(index, state.matches[state.selectedIndex]);
            }
            break;
            
        case 'Escape':
            e.preventDefault();
            hideAutocomplete(index);
            break;
    }
}

// 選択項目の更新
function updateSelectedItem(index) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    const items = autocompleteDiv.querySelectorAll('.autocomplete-item');
    const state = autocompleteStates[index-1];
    
    items.forEach((item, i) => {
        if (i === state.selectedIndex) {
            item.classList.add('selected');
        } else {
            item.classList.remove('selected');
        }
    });
}

// モンスター選択
function selectMonster(index, name) {
    const input = document.getElementById(`monster${index}-input`);
    
    input.value = name;
    selectedMonsters[index-1] = name;
    
    hideAutocomplete(index);
    toggleResistanceLevel(index, true);
    updateDisplay();
}

// オートコンプリートを隠す
function hideAutocomplete(index) {
    const autocompleteDiv = document.getElementById(`monster${index}-autocomplete`);
    autocompleteDiv.style.display = 'none';
    const combo = document.getElementById(`monster${index}-combo`);
    combo.classList.remove('open');
    dropdownStates[index-1] = false;
    autocompleteStates[index-1] = {};
}

// 耐性レベル選択の表示/非表示
function toggleResistanceLevel(index, show) {
    const element = document.getElementById(`resistance${index}`);
    element.style.display = show ? 'block' : 'none';
}

// 統計情報の更新
function updateStats() {
    const totalCount = Object.keys(monstersData).length;
    document.getElementById('total-count').textContent = `${totalCount}体`;
    
    // 系統別集計
    const systemCount = {};
    Object.values(monstersData).forEach(monster => {
        const system = monster.系統 || '未知';
        systemCount[system] = (systemCount[system] || 0) + 1;
    });
    
    const breakdown = document.getElementById('system-breakdown');
    breakdown.innerHTML = Object.entries(systemCount)
        .sort()
        .map(([system, count]) => `<div>・${system}: ${count}体</div>`)
        .join('');
}

// 表示の更新
function updateDisplay() {
    const validMonsters = selectedMonsters.filter(m => m !== '');
    const count = validMonsters.length;
    
    // メッセージの制御
    const infoMessage = document.getElementById('info-message');
    const analysisSection = document.getElementById('analysis-section');
    const singleAnalysis = document.getElementById('single-analysis');
    
    if (count === 0) {
        infoMessage.style.display = 'block';
        analysisSection.style.display = 'none';
        singleAnalysis.style.display = 'none';
    } else if (count === 1) {
        infoMessage.style.display = 'none';
        analysisSection.style.display = 'none';
        singleAnalysis.style.display = 'block';
        updateSingleAnalysis(validMonsters[0], resistanceLevels[selectedMonsters.indexOf(validMonsters[0])]);
    } else {
        infoMessage.style.display = 'none';
        analysisSection.style.display = 'block';
        singleAnalysis.style.display = 'none';
        updateComparisonAnalysis(validMonsters);
    }
    
    // モンスターカードの表示
    updateMonsterCards(validMonsters);
}

// 単体分析の更新
function updateSingleAnalysis(monsterName, resistanceLevel) {
    const monster = monstersData[monsterName];
    
    document.getElementById('single-analysis-title').textContent = 
        `🎯 耐性分析 (${monsterName} - 耐性レベル: ${resistanceLevel})`;
    
    if (!monster.耐性 || !monster.耐性.説明) {
        document.getElementById('single-effective').innerHTML = '<div class="info">耐性情報がありません</div>';
        document.getElementById('single-ineffective').innerHTML = '';
        return;
    }
    
    const resistanceInfo = parseResistanceInfo(monster.耐性.説明);
    const analysis = analyzeSingleMonster(resistanceInfo, resistanceLevel);
    
    // 効果的な攻撃
    const effectiveContainer = document.getElementById('single-effective');
    effectiveContainer.innerHTML = '';
    
    if (analysis.weakness.length > 0) {
        analysis.weakness.forEach(attr => {
            const card = createAttackCard(attr, 'weakness', '🔥');
            effectiveContainer.appendChild(card);
        });
    }
    
    if (analysis.normal.length > 0) {
        analysis.normal.forEach(attr => {
            const card = createAttackCard(attr, 'effective', '⚡');
            effectiveContainer.appendChild(card);
        });
    }
    
    if (analysis.weakness.length === 0 && analysis.normal.length === 0) {
        effectiveContainer.innerHTML = '<div class="info">効果的な攻撃がありません</div>';
    }
    
    // 非効果的な攻撃
    const ineffectiveContainer = document.getElementById('single-ineffective');
    ineffectiveContainer.innerHTML = '';
    
    if (analysis.half.length > 0) {
        analysis.half.forEach(attr => {
            const card = createAttackCard(attr, 'half-damage', '🔽');
            ineffectiveContainer.appendChild(card);
        });
    }
    
    if (analysis.null.length > 0) {
        analysis.null.forEach(attr => {
            const card = createAttackCard(attr, 'ineffective', '❌');
            ineffectiveContainer.appendChild(card);
        });
    }
    
    if (analysis.half.length === 0 && analysis.null.length === 0) {
        ineffectiveContainer.innerHTML = '<div class="info">すべての攻撃が有効です！</div>';
    }
}

// 比較分析の更新
function updateComparisonAnalysis(validMonsters) {
    const analysis = analyzeCommonWeaknesses(validMonsters);
    
    // 効果的な攻撃
    const effectiveContainer = document.getElementById('effective-attacks');
    effectiveContainer.innerHTML = '';
    
    if (analysis.effective.length > 0) {
        analysis.effective.forEach(attack => {
            const isWeakness = attack.includes('弱点');
            const attr = attack.replace(/🔥|⚡/g, '').trim();
            const icon = isWeakness ? '🔥' : '⚡';
            const type = isWeakness ? 'weakness' : 'effective';
            const card = createAttackCard(attr, type, icon);
            effectiveContainer.appendChild(card);
        });
    } else {
        effectiveContainer.innerHTML = '<div class="info">全員に共通して効きやすい攻撃が見つかりませんでした</div>';
    }
    
    // 非効果的な攻撃
    const ineffectiveContainer = document.getElementById('ineffective-attacks');
    ineffectiveContainer.innerHTML = '';
    
    if (analysis.ineffective.length > 0) {
        analysis.ineffective.forEach(attack => {
            let type, icon;
            if (attack.includes('無効')) {
                type = 'ineffective';
                icon = '❌';
            } else {
                type = 'half-damage';
                icon = '🔽';
            }
            const card = createAttackCard(attack, type, icon);
            ineffectiveContainer.appendChild(card);
        });
    } else {
        ineffectiveContainer.innerHTML = '<div class="info">注意すべき攻撃はありません</div>';
    }
    
    // 詳細分析表
    updateDetailedAnalysis(analysis.details);
}

// 攻撃カードの作成
function createAttackCard(text, type, icon) {
    const card = document.createElement('div');
    card.className = `attack-card ${type}`;
    card.innerHTML = `<strong>${icon} ${text}</strong>`;
    return card;
}

// 詳細分析表の更新
function updateDetailedAnalysis(details) {
    const container = document.getElementById('detailed-analysis');
    
    if (!details || Object.keys(details).length === 0) {
        container.innerHTML = '<div class="info">詳細分析データがありません</div>';
        return;
    }
    
    let tableHTML = `
        <table class="resistance-table">
            <thead>
                <tr>
                    <th>属性</th>
                    ${selectedMonsters.filter(m => m).map(name => `<th>${name}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
    `;
    
    Object.entries(details).forEach(([attr, monsters]) => {
        tableHTML += `<tr><td><strong>${attr}</strong></td>`;
        selectedMonsters.filter(m => m).forEach(monsterName => {
            const resistance = monsters.find(m => m.startsWith(monsterName));
            const status = resistance ? resistance.split(':')[1] : '不明';
            tableHTML += `<td>${status}</td>`;
        });
        tableHTML += '</tr>';
    });
    
    tableHTML += '</tbody></table>';
    container.innerHTML = tableHTML;
}

// モンスターカードの更新
function updateMonsterCards(validMonsters) {
    const container = document.getElementById('monster-cards');
    container.innerHTML = '';
    
    validMonsters.forEach(monsterName => {
        const monster = monstersData[monsterName];
        const card = createMonsterCard(monsterName, monster);
        container.appendChild(card);
    });
}

// モンスターカードの作成
function createMonsterCard(name, data) {
    const card = document.createElement('div');
    card.className = 'monster-card';
    
    const systemColors = {
        '自然系': '#28a745',
        '魔獣系': '#6f42c1',
        '物質系': '#6c757d',
        '悪魔系': '#dc3545',
        'ドラゴン系': '#fd7e14',
        'スライム系': '#007bff',
        'ゾンビ系': '#343a40',
        '？？？系': '#e83e8c',
        '特殊系（魔王）': '#dc3545',
        '特殊系（神獣）': '#ffc107'
    };
    
    const systemColor = systemColors[data.系統] || '#6c757d';
    
    card.innerHTML = `
        <div class="monster-header" style="background: linear-gradient(135deg, #007bff, ${systemColor});">
            <h3>🐉 ${name}</h3>
            <div class="monster-system">【${data.系統 || '未知'}】</div>
        </div>
        <div class="monster-content">
            ${createTraitsSection(data.特性)}
            ${createResistanceSection(data.耐性)}
            ${createSkillsSection(data.スキル)}
        </div>
    `;
    
    return card;
}

// 特性セクション作成
function createTraitsSection(traits) {
    if (!traits || traits.length === 0) {
        return '';
    }
    
    return `
        <div class="monster-section">
            <h4>🔹 特性</h4>
            ${traits.map(trait => `<div>・<strong>${trait}</strong></div>`).join('')}
        </div>
    `;
}

// 耐性セクション作成
function createResistanceSection(resistance) {
    if (!resistance || !resistance.説明) {
        return '';
    }
    
    const resistanceInfo = parseResistanceInfo(resistance.説明);
    
    return `
        <div class="monster-section">
            <h4>🛡️ 耐性情報</h4>
            <table class="resistance-table">
                <thead>
                    <tr>
                        <th>💥 弱点</th>
                        <th>🛡️ 半減</th>
                        <th>✨ 無効</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>${createResistanceTags(resistanceInfo.弱点, 'weakness-tag')}</td>
                        <td>${createResistanceTags(resistanceInfo.半減, 'half-tag')}</td>
                        <td>${createResistanceTags(resistanceInfo.無効, 'null-tag')}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// 耐性タグ作成
function createResistanceTags(items, className) {
    if (!items || items.length === 0) {
        return '<span style="color: #6c757d; font-style: italic;">なし</span>';
    }
    
    return items.map(item => {
        let displayText = item;
        if (item.startsWith('◆◆')) {
            displayText = `${item.substring(2)} ★★`;
        } else if (item.startsWith('◆')) {
            displayText = `${item.substring(1)} ★`;
        }
        return `<span class="resistance-tag ${className}">${displayText}</span>`;
    }).join(' ');
}

// スキルセクション作成
function createSkillsSection(skills) {
    if (!skills || skills.length === 0) {
        return '';
    }
    
    return `
        <div class="monster-section">
            <h4>⚔️ スキル情報</h4>
            <div class="skills-list">
                ${skills.map(skill => `
                    <div class="skill-item">
                        <div class="skill-name">📚 ${skill.スキル名}</div>
                        ${skill.特技.map(technique => `
                            <div class="technique">
                                <strong>🗡️ ${technique.技名}</strong>
                                <span style="background-color: #007bff; color: white; padding: 1px 4px; border-radius: 8px; font-size: 0.7rem;">
                                    SP: ${technique.SP}
                                </span>
                                <div style="color: #666; font-size: 0.75rem;">${technique.効果}</div>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// 耐性情報の解析
function parseResistanceInfo(resistanceText) {
    const resistances = {
        '弱点': [],
        '半減': [],
        '無効': []
    };
    
    const lines = resistanceText.split('\n');
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        if (line.includes('弱い')) {
            const weakPart = line.includes('に弱い') ? line.split('に弱い')[0] : line.split('が弱い')[0];
            const weakAttrs = weakPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
            resistances['弱点'].push(...weakAttrs);
        }
        
        if (line.includes('半減')) {
            let halfPart = line.includes('を半減') ? line.split('を半減')[0] : line.split('が半減')[0];
            if (line.includes('（強の場合）')) {
                halfPart = halfPart.replace('（強の場合）', '').trim();
                const halfAttrs = halfPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['半減'].push(...halfAttrs.map(attr => `◆${attr}`));
            } else if (line.includes('（最強の場合）')) {
                halfPart = halfPart.replace('（最強の場合）', '').trim();
                const halfAttrs = halfPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['半減'].push(...halfAttrs.map(attr => `◆◆${attr}`));
            } else {
                const halfAttrs = halfPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['半減'].push(...halfAttrs);
            }
        }
        
        if (line.includes('無効')) {
            let nullPart = line.includes('を無効') ? line.split('を無効')[0] : line.split('が無効')[0];
            if (line.includes('（強の場合）')) {
                nullPart = nullPart.replace('（強の場合）', '').trim();
                const nullAttrs = nullPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['無効'].push(...nullAttrs.map(attr => `◆${attr}`));
            } else if (line.includes('（最強の場合）')) {
                nullPart = nullPart.replace('（最強の場合）', '').trim();
                const nullAttrs = nullPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['無効'].push(...nullAttrs.map(attr => `◆◆${attr}`));
            } else {
                const nullAttrs = nullPart.replace(/・/g, '・').split('・').map(s => s.trim()).filter(s => s);
                resistances['無効'].push(...nullAttrs);
            }
        }
    });
    
    return resistances;
}

// 単体モンスター分析
function analyzeSingleMonster(resistanceInfo, resistanceLevel) {
    const allAttributes = [
        // 呪文系
        'メラ', 'ギラ', 'ヒャド', 'バギ', 'イオ', 'デイン', 'ドルマ',
        // ブレス系
        '炎ブレス', '吹雪', '吹雪ブレス',
        // 即死・状態異常
        'ザキ', 'マヒ', '眠り', '混乱', '毒', '休み',
        // 能力低下系
        'ルカニ', 'ダウン', 'ボミエ', 'フール', 'マインド', 'ベタン',
        // 封じ系
        'マホトーン', '体技封じ', '息封じ', '斬撃封じ', '踊り封じ',
        // その他
        'マホトラ', 'ハック', 'マヌーサ', '踊り'
    ];
    
    const analysis = {
        weakness: [],
        normal: [],
        half: [],
        null: []
    };
    
    allAttributes.forEach(attr => {
        const isWeak = resistanceInfo.弱点.some(weak => weak.includes(attr));
        
        let isHalf = false;
        let isNull = false;
        
        // 半減チェック
        resistanceInfo.半減.forEach(half => {
            const cleanHalf = half.replace(/◆/g, '');
            if (cleanHalf.includes(attr)) {
                // 通常レベル：◆なしの半減 + 強・最強でも適用
                if (!half.includes('◆')) {
                    isHalf = true;
                }
                // 強レベル：◆ありの半減も追加で適用
                else if (resistanceLevel === '強' && half.includes('◆') && !half.includes('◆◆')) {
                    isHalf = true;
                }
                // 最強レベル：◆◆ありの半減も追加で適用
                else if (resistanceLevel === '最強' && half.includes('◆◆')) {
                    isHalf = true;
                }
            }
        });
        
        // 無効チェック
        resistanceInfo.無効.forEach(null_item => {
            const cleanNull = null_item.replace(/◆/g, '');
            if (cleanNull.includes(attr)) {
                // 通常レベル：◆なしの無効 + 強・最強でも適用
                if (!null_item.includes('◆')) {
                    isNull = true;
                }
                // 強レベル：◆ありの無効も追加で適用
                else if (resistanceLevel === '強' && null_item.includes('◆') && !null_item.includes('◆◆')) {
                    isNull = true;
                }
                // 最強レベル：◆◆ありの無効も追加で適用
                else if (resistanceLevel === '最強' && null_item.includes('◆◆')) {
                    isNull = true;
                }
            }
        });
        
        if (isWeak) {
            analysis.weakness.push(attr);
        } else if (isNull) {
            analysis.null.push(attr);
        } else if (isHalf) {
            analysis.half.push(attr);
        } else {
            analysis.normal.push(attr);
        }
    });
    
    return analysis;
}

// 共通弱点分析
function analyzeCommonWeaknesses(validMonsters) {
    const allAttributes = [
        // 呪文系
        'メラ', 'ギラ', 'ヒャド', 'バギ', 'イオ', 'デイン', 'ドルマ',
        // ブレス系
        '炎ブレス', '吹雪', '吹雪ブレス',
        // 即死・状態異常
        'ザキ', 'マヒ', '眠り', '混乱', '毒', '休み',
        // 能力低下系
        'ルカニ', 'ダウン', 'ボミエ', 'フール', 'マインド', 'ベタン',
        // 封じ系
        'マホトーン', '体技封じ', '息封じ', '斬撃封じ', '踊り封じ',
        // その他
        'マホトラ', 'ハック', 'マヌーサ', '踊り'
    ];
    
    const effectiveAttacks = [];
    const ineffectiveAttacks = [];
    const details = {};
    
    allAttributes.forEach(attr => {
        const resistanceDetails = [];
        let effectiveForAll = true;
        let hasWeakness = false;
        let nullCount = 0;
        let halfCount = 0;
        
        validMonsters.forEach((monsterName, index) => {
            const monster = monstersData[monsterName];
            const resistanceLevel = resistanceLevels[selectedMonsters.indexOf(monsterName)];
            
            if (monster.耐性 && monster.耐性.説明) {
                const resistanceInfo = parseResistanceInfo(monster.耐性.説明);
                
                const isWeak = resistanceInfo.弱点.some(weak => weak.includes(attr));
                let isHalf = false;
                let isNull = false;
                
                // 半減判定
                resistanceInfo.半減.forEach(half => {
                    const cleanHalf = half.replace(/◆/g, '');
                    if (cleanHalf.includes(attr)) {
                        // 通常レベル：◆なしの半減 + 強・最強でも適用
                        if (!half.includes('◆')) {
                            isHalf = true;
                        }
                        // 強レベル：◆ありの半減も追加で適用
                        else if (resistanceLevel === '強' && half.includes('◆') && !half.includes('◆◆')) {
                            isHalf = true;
                        }
                        // 最強レベル：◆◆ありの半減も追加で適用
                        else if (resistanceLevel === '最強' && half.includes('◆◆')) {
                            isHalf = true;
                        }
                    }
                });
                
                // 無効判定
                resistanceInfo.無効.forEach(null_item => {
                    const cleanNull = null_item.replace(/◆/g, '');
                    if (cleanNull.includes(attr)) {
                        // 通常レベル：◆なしの無効 + 強・最強でも適用
                        if (!null_item.includes('◆')) {
                            isNull = true;
                        }
                        // 強レベル：◆ありの無効も追加で適用
                        else if (resistanceLevel === '強' && null_item.includes('◆') && !null_item.includes('◆◆')) {
                            isNull = true;
                        }
                        // 最強レベル：◆◆ありの無効も追加で適用
                        else if (resistanceLevel === '最強' && null_item.includes('◆◆')) {
                            isNull = true;
                        }
                    }
                });
                
                if (isNull) {
                    resistanceDetails.push(`${monsterName}(${resistanceLevel}):無効`);
                    effectiveForAll = false;
                    nullCount++;
                } else if (isHalf) {
                    resistanceDetails.push(`${monsterName}(${resistanceLevel}):半減`);
                    effectiveForAll = false;
                    halfCount++;
                } else if (isWeak) {
                    resistanceDetails.push(`${monsterName}(${resistanceLevel}):弱点`);
                    hasWeakness = true;
                } else {
                    resistanceDetails.push(`${monsterName}(${resistanceLevel}):通常`);
                }
            } else {
                resistanceDetails.push(`${monsterName}(${resistanceLevel}):情報なし`);
            }
        });
        
        // 効果的な攻撃の判定
        if (effectiveForAll) {
            if (hasWeakness) {
                effectiveAttacks.push(`🔥 ${attr} (弱点)`);
            } else {
                effectiveAttacks.push(`⚡ ${attr}`);
            }
        }
        
        // 非効果的な攻撃の判定
        if (nullCount > 0) {
            if (nullCount === validMonsters.length) {
                ineffectiveAttacks.push(`❌ ${attr} (全員無効)`);
            } else {
                ineffectiveAttacks.push(`❌ ${attr} (無効×${nullCount})`);
            }
        } else if (halfCount > 0) {
            if (halfCount === validMonsters.length) {
                ineffectiveAttacks.push(`🔽 ${attr} (全員半減)`);
            } else {
                ineffectiveAttacks.push(`📉 ${attr} (半減×${halfCount})`);
            }
        }
        
        details[attr] = resistanceDetails;
    });
    
    return {
        effective: effectiveAttacks,
        ineffective: ineffectiveAttacks,
        details: details
    };
}

// ローディング表示制御
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('main-display').style.display = 'block';
}

function showError() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('error').style.display = 'block';
}
