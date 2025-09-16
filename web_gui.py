#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DQMJ2 モンスター情報比較ツール - Streamlit Web版
ブラウザで動作する最もモダンなバージョン
"""

import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any

# データファイルのパス
DATA_FILE = "dqmj2_monsters.json"

@st.cache_data
def load_monster_data():
    """モンスターデータを読み込み（キャッシュ付き）"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def parse_resistance_info(resistance_text: str) -> Dict[str, List[str]]:
    """耐性情報を解析"""
    resistances = {
        "弱点": [],
        "半減": [],
        "無効": []
    }
    
    lines = resistance_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "弱い" in line:
            weak_part = line.split("に弱い")[0] if "に弱い" in line else line.split("が弱い")[0]
            weak_attrs = [attr.strip() for attr in weak_part.replace("・", "・").split("・") if attr.strip()]
            resistances["弱点"].extend(weak_attrs)
            
        elif "半減" in line:
            if "（強の場合）" in line:
                half_part = line.split("を半減")[0] if "を半減" in line else line.split("が半減")[0]
                half_part = half_part.replace("（強の場合）", "").strip()
                half_attrs = [f"◆{attr.strip()}" for attr in half_part.replace("・", "・").split("・") if attr.strip()]
                resistances["半減"].extend(half_attrs)
            else:
                half_part = line.split("を半減")[0] if "を半減" in line else line.split("が半減")[0]
                half_attrs = [attr.strip() for attr in half_part.replace("・", "・").split("・") if attr.strip()]
                resistances["半減"].extend(half_attrs)
                
        elif "無効" in line:
            if "（最強の場合）" in line:
                null_part = line.split("を無効")[0] if "を無効" in line else line.split("が無効")[0]
                null_part = null_part.replace("（最強の場合）", "").strip()
                null_attrs = [f"◆◆{attr.strip()}" for attr in null_part.replace("・", "・").split("・") if attr.strip()]
                resistances["無効"].extend(null_attrs)
            else:
                null_part = line.split("を無効")[0] if "を無効" in line else line.split("が無効")[0]
                null_attrs = [attr.strip() for attr in null_part.replace("・", "・").split("・") if attr.strip()]
                resistances["無効"].extend(null_attrs)
    
    return resistances

def display_monster_card(monster_name: str, monster_data: Dict[str, Any]):
    """モンスター情報カードを表示"""
    if not monster_data:
        st.info("モンスターを選択してください")
        return
    
    # モンスター名と系統
    system_name = monster_data.get("系統", "未知")
    system_color = {
        "自然系": "#28a745",
        "魔獣系": "#6f42c1", 
        "物質系": "#6c757d",
        "悪魔系": "#dc3545",
        "ドラゴン系": "#fd7e14",
        "スライム系": "#007bff",
        "ゾンビ系": "#343a40",
        "？？？系": "#e83e8c",
        "特殊系（魔王）": "#dc3545",
        "特殊系（神獣）": "#ffc107"
    }.get(system_name, "#6c757d")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #007bff, {system_color}); 
                color: white; 
                padding: 15px; 
                border-radius: 10px; 
                text-align: center; 
                margin-bottom: 20px;">
        <h2>🐉 {monster_name}</h2>
        <div style="background-color: rgba(255,255,255,0.2); 
                    display: inline-block; 
                    padding: 5px 15px; 
                    border-radius: 20px; 
                    margin-top: 8px;">
            <strong>【{system_name}】</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 特性
    if monster_data.get("特性"):
        st.markdown("### 🔹 特性")
        for trait in monster_data["特性"]:
            st.markdown(f"- **{trait}**")
        st.markdown("---")
    
    # 耐性
    if monster_data.get("耐性") and monster_data["耐性"].get("説明"):
        st.markdown("### 🛡️ 耐性情報")
        
        resistance_info = parse_resistance_info(monster_data["耐性"]["説明"])
        
        # テーブル形式で表示
        table_html = """
        <div style="background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden; margin: 10px 0;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                <thead>
                    <tr style="background-color: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                        <th style="padding: 8px 12px; text-align: center; font-weight: bold; color: #495057; border-right: 1px solid #dee2e6;">💥 弱点</th>
                        <th style="padding: 8px 12px; text-align: center; font-weight: bold; color: #495057; border-right: 1px solid #dee2e6;">🛡️ 半減</th>
                        <th style="padding: 8px 12px; text-align: center; font-weight: bold; color: #495057;">✨ 無効</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
        """
        
        # 弱点セル
        table_html += '<td style="padding: 12px; vertical-align: top; border-right: 1px solid #dee2e6; background-color: #fff5f5;">'
        if resistance_info["弱点"]:
            for weak in resistance_info["弱点"]:
                table_html += f'<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 15px; margin: 2px; display: inline-block; font-size: 11px;">{weak}</span>'
        else:
            table_html += '<span style="color: #6c757d; font-style: italic;">なし</span>'
        table_html += '</td>'
        
        # 半減セル
        table_html += '<td style="padding: 12px; vertical-align: top; border-right: 1px solid #dee2e6; background-color: #fff9f0;">'
        if resistance_info["半減"]:
            for half in resistance_info["半減"]:
                if half.startswith("◆"):
                    color = "#6f42c1"  # 紫色（強）
                    text = f"{half[1:]} ★"
                else:
                    color = "#fd7e14"  # オレンジ色
                    text = half
                table_html += f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 15px; margin: 2px; display: inline-block; font-size: 11px;">{text}</span>'
        else:
            table_html += '<span style="color: #6c757d; font-style: italic;">なし</span>'
        table_html += '</td>'
        
        # 無効セル
        table_html += '<td style="padding: 12px; vertical-align: top; background-color: #f0fff4;">'
        if resistance_info["無効"]:
            for null in resistance_info["無効"]:
                if null.startswith("◆◆"):
                    color = "#dc3545"  # 赤色（最強）
                    text = f"{null[2:]} ★★"
                else:
                    color = "#28a745"  # 緑色
                    text = null
                table_html += f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 15px; margin: 2px; display: inline-block; font-size: 11px;">{text}</span>'
        else:
            table_html += '<span style="color: #6c757d; font-style: italic;">なし</span>'
        table_html += '</td>'
        
        table_html += """
                    </tr>
                </tbody>
            </table>
        </div>
        """
        
        # 凡例を追加
        legend_html = """
        <div style="margin: 10px 0; padding: 8px; background-color: #f8f9fa; border-radius: 5px; font-size: 11px;">
            <strong>📋 凡例:</strong> 
            <span style="color: #6f42c1;">★ = 強の特性で半減</span> | 
            <span style="color: #dc3545;">★★ = 最強の特性で無効</span>
        </div>
        """
        
        st.markdown(table_html + legend_html, unsafe_allow_html=True)
        st.markdown("---")
    
    # スキル
    if monster_data.get("スキル"):
        st.markdown("### ⚔️ スキル情報")
        
        for skill in monster_data["スキル"]:
            with st.expander(f"📚 {skill['スキル名']}", expanded=True):
                for technique in skill["特技"]:
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; 
                                border-left: 4px solid #007bff; 
                                padding: 10px; 
                                margin: 5px 0; 
                                border-radius: 0 5px 5px 0;">
                        <strong>🗡️ {technique['技名']}</strong> 
                        <span style="background-color: #007bff; 
                                     color: white; 
                                     padding: 2px 6px; 
                                     border-radius: 10px; 
                                     font-size: 0.8rem;">
                            SP: {technique['SP']}
                        </span>
                        <p style="margin-top: 5px; color: #666;">{technique['効果']}</p>
                    </div>
                    """, unsafe_allow_html=True)

def analyze_common_weaknesses(selected_monsters: List[str], monsters_data: Dict[str, Any], resistance_levels: List[str]) -> Dict[str, List[str]]:
    """選択されたモンスター全員に共通する弱点・効きやすい攻撃を分析（モンスターごとの耐性レベル対応）"""
    if len(selected_monsters) < 2:
        return {"effective_attacks": [], "ineffective_attacks": [], "explanation": []}
    
    # 有効なモンスターのみフィルタ
    valid_monsters = []
    valid_levels = []
    for i, monster in enumerate(selected_monsters):
        if monster and monster in monsters_data:
            valid_monsters.append(monster)
            valid_levels.append(resistance_levels[i] if i < len(resistance_levels) else "通常")
    
    if len(valid_monsters) < 2:
        return {"effective_attacks": [], "ineffective_attacks": [], "explanation": []}
    
    all_attributes = ["メラ", "ギラ", "ヒャド", "バギ", "イオ", "デイン", "ドルマ", "ザキ", "マヒ", "眠り", "混乱", "毒", "マホトーン"]
    
    effective_attacks = []
    ineffective_attacks = []
    resistance_summary = {}
    
    # 各属性に対する全モンスターの耐性を調査
    for attr in all_attributes:
        is_effective_for_all = True
        is_ineffective_for_all = True
        resistance_details = []
        
        for i, monster_name in enumerate(valid_monsters):
            monster_data = monsters_data[monster_name]
            resistance_level = valid_levels[i]
            if monster_data.get("耐性") and monster_data["耐性"].get("説明"):
                resistance_info = parse_resistance_info(monster_data["耐性"]["説明"])
                
                # この属性に対する耐性をチェック
                is_weak = any(attr in weak for weak in resistance_info["弱点"])
                
                # 耐性レベルに応じた半減・無効判定
                is_half = False
                is_null = False
                
                for half in resistance_info["半減"]:
                    clean_half = half.replace("◆", "")
                    if attr in clean_half:
                        if resistance_level == "通常":
                            is_half = True
                        elif resistance_level == "強" and "◆" in half:
                            is_half = True
                        elif resistance_level == "最強":
                            is_half = True
                
                for null in resistance_info["無効"]:
                    clean_null = null.replace("◆", "")
                    if attr in clean_null:
                        if resistance_level == "通常":
                            is_null = True
                        elif resistance_level == "強" and "◆" in null:
                            is_null = True
                        elif resistance_level == "最強" and "◆◆" in null:
                            is_null = True
                
                if is_null:
                    resistance_details.append(f"{monster_name}({resistance_level}):無効")
                    is_effective_for_all = False
                elif is_half:
                    resistance_details.append(f"{monster_name}({resistance_level}):半減")
                    is_effective_for_all = False
                    is_ineffective_for_all = False
                elif is_weak:
                    resistance_details.append(f"{monster_name}({resistance_level}):弱点")
                    is_ineffective_for_all = False
                else:
                    resistance_details.append(f"{monster_name}({resistance_level}):通常")
                    is_ineffective_for_all = False
            else:
                resistance_details.append(f"{monster_name}({resistance_level}):情報なし")
                is_ineffective_for_all = False
        
        # 効果的な攻撃の判定
        if is_effective_for_all:
            weak_count = sum(1 for detail in resistance_details if "弱点" in detail)
            if weak_count > 0:
                effective_attacks.append(f"🔥 {attr} (弱点×{weak_count})")
            else:
                effective_attacks.append(f"⚡ {attr}")
        
        # 非効果的な攻撃の判定
        if any("無効" in detail for detail in resistance_details):
            null_count = sum(1 for detail in resistance_details if "無効" in detail)
            if null_count == len(valid_monsters):
                ineffective_attacks.append(f"❌ {attr} (全員無効)")
            else:
                ineffective_attacks.append(f"� {attr} (無効×{null_count})")
        elif any("半減" in detail for detail in resistance_details):
            half_count = sum(1 for detail in resistance_details if "半減" in detail)
            if half_count == len(valid_monsters):
                ineffective_attacks.append(f"🔽 {attr} (全員半減)")
            else:
                ineffective_attacks.append(f"📉 {attr} (半減×{half_count})")
        
        resistance_summary[attr] = resistance_details
    
    return {
        "effective_attacks": effective_attacks,
        "ineffective_attacks": ineffective_attacks,
        "resistance_summary": resistance_summary,
        "valid_monsters": valid_monsters,
        "resistance_levels": valid_levels
    }

def create_comparison_table(selected_monsters: List[str], monsters_data: Dict[str, Any]):
    """比較テーブルを作成"""
    if not any(selected_monsters):
        st.info("比較するモンスターを選択してください")
        return
    
    comparison_data = []
    
    # 各カテゴリのデータを収集
    categories = ["系統", "特性", "弱点", "半減", "無効", "スキル数"]
    
    for monster_name in selected_monsters:
        if not monster_name or monster_name not in monsters_data:
            continue
            
        data = monsters_data[monster_name]
        row = {"モンスター": monster_name}
        
        # 系統
        row["系統"] = data.get("系統", "未知")
        
        # 特性
        traits = data.get("特性", [])
        row["特性"] = "、".join(traits) if traits else "なし"
        
        # 耐性情報
        if data.get("耐性") and data["耐性"].get("説明"):
            resistance_info = parse_resistance_info(data["耐性"]["説明"])
            row["弱点"] = "、".join(resistance_info["弱点"]) if resistance_info["弱点"] else "なし"
            row["半減"] = "、".join(resistance_info["半減"]) if resistance_info["半減"] else "なし"
            row["無効"] = "、".join(resistance_info["無効"]) if resistance_info["無効"] else "なし"
        else:
            row["弱点"] = "情報なし"
            row["半減"] = "情報なし"
            row["無効"] = "情報なし"
        
        # スキル数
        skills = data.get("スキル", [])
        total_techniques = sum(len(skill["特技"]) for skill in skills)
        row["スキル数"] = f"{len(skills)}スキル / {total_techniques}特技"
        
        comparison_data.append(row)
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)

def main():
    """メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title="DQMJ2 モンスター比較ツール",
        page_icon="🐉",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #007bff;
        font-size: 12px;
    }
    .stExpander {
        font-size: 11px;
    }
    .stMarkdown {
        font-size: 12px;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.4rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    h4 {
        font-size: 0.9rem !important;
    }
    p {
        font-size: 12px !important;
    }
    .element-container {
        font-size: 12px;
    }
    .stDataFrame {
        font-size: 11px;
    }
    .stButton > button {
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # タイトル
    st.markdown("""
    <div style="background: linear-gradient(90deg, #007bff, #6f42c1); 
                color: white; 
                padding: 20px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 20px;">
        <h1 style="font-size: 1.8rem; margin: 0;">🐉 DQMJ2 モンスター情報比較ツール</h1>
        <p style="font-size: 1.0rem; margin: 5px 0 0 0;">Web Edition - ブラウザで簡単比較</p>
    </div>
    """, unsafe_allow_html=True)
    
    # データ読み込み
    monsters_data = load_monster_data()
    
    if not monsters_data:
        st.error("⚠️ モンスターデータが見つかりません。`dqmj2_monsters.json`ファイルを確認してください。")
        st.info("💡 データをスクレイピングするには、`main.py`を実行してください。")
        return
    
    monster_names = sorted(list(monsters_data.keys()))
    
    # サイドバー
    with st.sidebar:
        st.markdown("## 🎮 操作パネル")
        
        st.markdown("### 📊 比較モンスター選択")
        st.markdown("最大3体まで選択可能")
        
        compare_monsters = []
        resistance_levels = []
        
        for i in range(3):
            monster = st.selectbox(
                f"モンスター {i+1}",
                options=[""] + monster_names,
                key=f"compare_{i}",
                help=f"{i+1}番目の比較モンスターを選択"
            )
            compare_monsters.append(monster)
            
            # モンスターが選択されている場合のみ耐性レベル選択を表示
            if monster:
                resistance_level = st.radio(
                    f"モンスター{i+1}の耐性レベル",
                    ["通常", "強", "最強"],
                    index=0,
                    key=f"resistance_{i}",
                    help=f"{monster}の特性による耐性変化を選択"
                )
                resistance_levels.append(resistance_level)
            else:
                resistance_levels.append("通常")
            
            if i < 2:  # 最後の要素以外に区切り線
                st.markdown("---")
        
        # 統計情報
        st.markdown("---")
        st.markdown("### 📈 データ統計")
        
        # 系統別集計
        system_count = {}
        for name, data in monsters_data.items():
            system = data.get("系統", "未知")
            system_count[system] = system_count.get(system, 0) + 1
        
        st.markdown(f"**総モンスター数:** {len(monsters_data)}体")
        
        with st.expander("系統別詳細", expanded=False):
            for system, count in sorted(system_count.items()):
                st.markdown(f"- {system}: {count}体")
    
    # メインコンテンツ
    st.markdown("## 📊 モンスター比較")
    
    # 選択されたモンスターの数を確認
    selected_count = sum(1 for monster in compare_monsters if monster)
    
    if selected_count >= 2:
        st.success(f"✅ {selected_count}体のモンスターを比較中")
        
        # 効果的な攻撃分析を追加
        if selected_count >= 2:
            st.markdown("### 🎯 攻撃効果分析")
            
            # サイドバーから各モンスターの耐性レベルを取得
            monster_resistance_levels = []
            for monster in compare_monsters:
                if monster:
                    # 該当するモンスターのサイドバーでの選択値を取得
                    level_key = f"resistance_level_{monster}"
                    level = st.session_state.get(level_key, "通常")
                    monster_resistance_levels.append(level)
                else:
                    monster_resistance_levels.append("通常")
            
            weakness_analysis = analyze_common_weaknesses(compare_monsters, monsters_data, monster_resistance_levels)
            
            # 効果的な攻撃を縦に表示
            st.markdown("#### ✅ 効果的な攻撃 (全員に効く)")
            if weakness_analysis["effective_attacks"]:
                # 効果的な攻撃をカード形式で表示
                cols = st.columns(min(4, len(weakness_analysis["effective_attacks"])))
                for i, attack in enumerate(weakness_analysis["effective_attacks"][:8]):
                    with cols[i % 4]:
                        if "弱点" in attack:
                            color = "#dc3545"  # 赤色（弱点有り）
                        else:
                            color = "#28a745"  # 緑色（通常有効）
                        
                        st.markdown(f"""
                        <div style="background-color: {color}; 
                                    color: white; 
                                    padding: 10px; 
                                    border-radius: 8px; 
                                    text-align: center; 
                                    margin: 5px 0;
                                    font-size: 12px;">
                            <strong>{attack}</strong>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ 全員に共通して効きやすい攻撃が見つかりませんでした。")
            
            # 非効果的な攻撃を縦に表示
            st.markdown("#### ❌ 非効果的な攻撃 (避けるべき攻撃)")
            if weakness_analysis["ineffective_attacks"]:
                # 非効果的な攻撃をカード形式で表示
                cols = st.columns(min(4, len(weakness_analysis["ineffective_attacks"])))
                for i, attack in enumerate(weakness_analysis["ineffective_attacks"][:8]):
                    with cols[i % 4]:
                        if "全員無効" in attack or "全員半減" in attack:
                            color = "#6c757d"  # グレー（全員）
                        elif "無効" in attack:
                            color = "#dc3545"  # 赤色（無効）
                        else:
                            color = "#fd7e14"  # オレンジ色（半減）
                        
                        st.markdown(f"""
                        <div style="background-color: {color}; 
                                    color: white; 
                                    padding: 10px; 
                                    border-radius: 8px; 
                                    text-align: center; 
                                    margin: 5px 0;
                                    font-size: 12px;">
                            <strong>{attack}</strong>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("💡 注意すべき攻撃はありません。")
            
            # 詳細分析を展開可能セクションで表示
            with st.expander("🔍 詳細な耐性分析表", expanded=False):
                analysis_df_data = []
                
                for attr, details in weakness_analysis["resistance_summary"].items():
                    row = {"属性": attr}
                    for detail in details:
                        monster_name, resistance = detail.split(":")
                        row[monster_name] = resistance
                    analysis_df_data.append(row)
                
                if analysis_df_data:
                    analysis_df = pd.DataFrame(analysis_df_data)
                    st.dataframe(analysis_df, use_container_width=True)
                    
                    # 凡例
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-size: 11px;">
                        <strong>📋 凡例 ({resistance_level}攻撃時):</strong> 
                        <span style="color: #dc3545;">🔥 = 弱点持ちに特に効果的</span> | 
                        <span style="color: #28a745;">⚡ = 全員に通常ダメージ</span> | 
                        <span style="color: #fd7e14;">📉 = 半減される</span> | 
                        <span style="color: #6c757d;">❌ = 無効化される</span><br>
                        <strong>効果順位:</strong> 弱点 > 通常 > 半減 > 無効
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # 比較テーブル
        create_comparison_table(compare_monsters, monsters_data)
        
        # 個別カード表示（横並び3列）
        st.markdown("### 🃏 詳細比較")
        
        # 選択されたモンスターのみフィルタ
        valid_monsters = [monster for monster in compare_monsters if monster]
        
        if valid_monsters:
            # 3列で表示
            cols = st.columns(3)
            for i, monster_name in enumerate(valid_monsters):
                with cols[i % 3]:
                    display_monster_card(monster_name, monsters_data.get(monster_name, {}))
    
    elif selected_count == 1:
        st.info("📋 1体のモンスター情報を表示しています（2体以上選択すると比較分析も表示されます）")
        
        # 1体の場合も詳細情報を表示
        valid_monsters = [monster for monster in compare_monsters if monster]
        
        if valid_monsters:
            monster_name = valid_monsters[0]
            
            # 選択されたモンスターの位置を特定して耐性レベルを取得
            monster_index = compare_monsters.index(monster_name)
            resistance_level = resistance_levels[monster_index] if monster_index < len(resistance_levels) else "通常"
            
            # 個別の耐性分析を表示
            st.markdown(f"### 🎯 耐性分析 (耐性レベル: {resistance_level})")
            monster_data = monsters_data[monster_name]
            
            if monster_data.get("耐性") and monster_data["耐性"].get("説明"):
                resistance_info = parse_resistance_info(monster_data["耐性"]["説明"])
                
                # 各属性に対する耐性を分析
                all_attributes = ["メラ", "ギラ", "ヒャド", "バギ", "イオ", "デイン", "ドルマ", "ザキ", "マヒ", "眠り", "混乱", "毒", "マホトーン"]
                
                effective_attrs = []
                weak_attrs = []
                ineffective_attrs = []
                
                for attr in all_attributes:
                    is_weak = any(attr in weak for weak in resistance_info["弱点"])
                    is_half = False
                    is_null = False
                    
                    # 耐性レベルに応じた判定
                    for half in resistance_info["半減"]:
                        clean_half = half.replace("◆", "")
                        if attr in clean_half:
                            if resistance_level == "通常":
                                is_half = True
                            elif resistance_level == "強" and "◆" in half:
                                is_half = True
                            elif resistance_level == "最強":
                                is_half = True
                    
                    for null in resistance_info["無効"]:
                        clean_null = null.replace("◆", "")
                        if attr in clean_null:
                            if resistance_level == "通常":
                                is_null = True
                            elif resistance_level == "強" and "◆" in null:
                                is_null = True
                            elif resistance_level == "最強" and "◆◆" in null:
                                is_null = True
                    
                    if is_weak:
                        weak_attrs.append(attr)
                    elif is_null:
                        ineffective_attrs.append(f"❌ {attr}")
                    elif is_half:
                        ineffective_attrs.append(f"🔽 {attr}")
                    else:
                        effective_attrs.append(attr)
                
                # カード形式で表示
                st.markdown("#### ✅ 効果的な攻撃")
                
                # 弱点攻撃
                if weak_attrs:
                    st.markdown("**🔥 弱点攻撃 (2倍ダメージ):**")
                    cols = st.columns(min(4, len(weak_attrs)))
                    for i, attr in enumerate(weak_attrs):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div style="background-color: #dc3545; 
                                        color: white; 
                                        padding: 8px; 
                                        border-radius: 8px; 
                                        text-align: center; 
                                        margin: 2px 0;
                                        font-size: 12px;">
                                <strong>🔥 {attr}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 通常攻撃
                if effective_attrs:
                    st.markdown("**⚡ 通常攻撃 (等倍ダメージ):**")
                    cols = st.columns(min(4, len(effective_attrs)))
                    for i, attr in enumerate(effective_attrs):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div style="background-color: #28a745; 
                                        color: white; 
                                        padding: 8px; 
                                        border-radius: 8px; 
                                        text-align: center; 
                                        margin: 2px 0;
                                        font-size: 12px;">
                                <strong>⚡ {attr}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 非効果的な攻撃
                st.markdown("#### ❌ 非効果的な攻撃")
                if ineffective_attrs:
                    cols = st.columns(min(4, len(ineffective_attrs)))
                    for i, attr in enumerate(ineffective_attrs):
                        with cols[i % 4]:
                            if "❌" in attr:
                                color = "#6c757d"  # 無効
                            else:
                                color = "#fd7e14"  # 半減
                            
                            st.markdown(f"""
                            <div style="background-color: {color}; 
                                        color: white; 
                                        padding: 8px; 
                                        border-radius: 8px; 
                                        text-align: center; 
                                        margin: 2px 0;
                                        font-size: 12px;">
                                <strong>{attr}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("💡 すべての攻撃が有効です！")
            else:
                st.warning("⚠️ この モンスターの耐性情報がありません。")
            
            st.markdown("---")
            
            # 比較テーブルも1体用に表示
            st.markdown("### 📊 基本情報")
            create_comparison_table(compare_monsters, monsters_data)
            
            # 個別カード表示
            st.markdown("### 🃏 詳細情報")
            display_monster_card(monster_name, monsters_data.get(monster_name, {}))
    else:
        st.info("👈 サイドバーから比較するモンスターを選択してください")

if __name__ == "__main__":
    main()
