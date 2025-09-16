"""
DQMJ2 モンスターデータスクレイピングツール

Webサイトから全モンスターのデータを取得してJSONファイルに保存するスクリプト
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# --- データ取得（スクレイピング）設定 ---
BASE_URL = "http://capch.net/dqmj2/book/"
DATA_FILE = "dqmj2_monsters.json"

def scrape_monster_data():
    """Webサイトから全モンスターのデータを取得してJSONファイルに保存する"""
    try:
        print("モンスターデータの取得を開始します...")
        
        # 全系統のプレフィックスを定義
        # DQMJ2の系統: 自然・魔獣・物質・悪魔・ドラゴン・スライム・ゾンビ・？？？・特殊系
        system_prefixes = {
            'si': '自然系',
            'm': '魔獣系', 
            'b': '物質系',
            'a': '悪魔系',
            'd': 'ドラゴン系',
            'sr': 'スライム系',
            'z': 'ゾンビ系',
            'p': '？？？系',
            'x': '特殊系（魔王）',
            'k': '特殊系（神獣）'
        }
        
        # 図鑑トップページから全モンスターのリンクを取得
        top_response = requests.get(BASE_URL)
        top_response.raise_for_status()
        top_soup = BeautifulSoup(top_response.content, 'html.parser')
        
        all_monster_links = []
        for prefix, system_name in system_prefixes.items():
            # 各系統のモンスターを取得
            system_links = [a['href'] for a in top_soup.select(f'a[href^="{prefix}-"]') if a['href'].endswith('.html')]
            print(f"{system_name}: {len(system_links)} 体のモンスターを発見")
            all_monster_links.extend([(link, system_name) for link in system_links])

        print(f"総モンスター数: {len(all_monster_links)} 体")
        
        if not all_monster_links:
            return {"error": "モンスターへのリンクが見つかりませんでした。"}

        all_monsters_data = {}
        processed_count = 0
        
        # 各モンスターの詳細ページからデータを取得
        for monster_link, system_name in all_monster_links:
            processed_count += 1
            monster_url = BASE_URL + monster_link
            print(f"進行状況 {processed_count}/{len(all_monster_links)}: {monster_link} ({system_name})")
            
            time.sleep(0.1)  # サーバーへの負荷軽減
            
            try:
                monster_response = requests.get(monster_url)
                monster_response.raise_for_status()
                monster_soup = BeautifulSoup(monster_response.content, 'html.parser')

                # モンスター名（動的セレクタ選択）
                name_element = None
                name = None
                
                # まず期待される系統のセレクタを試す
                system_selectors = {
                    '自然系': 'h2.sizen',
                    '魔獣系': 'h2.majyuu', 
                    '物質系': 'h2.bussitu',
                    '悪魔系': 'h2.akuma',
                    'ドラゴン系': 'h2.doragon',
                    'スライム系': 'h2.suraimu',
                    'ゾンビ系': 'h2.zonbi',
                    '？？？系': 'h2.akuma',  # ？？？系は悪魔系と同じセレクタ
                    '特殊系（魔王）': 'h2.majyuu',  # 魔王系は魔獣系と同じセレクタ
                    '特殊系（神獣）': 'h2.kami'
                }
                
                selector = system_selectors.get(system_name, 'h2')
                name_element = monster_soup.select_one(selector)
                
                # 期待されるセレクタで見つからない場合、全ての系統セレクタを試す
                if not name_element:
                    all_selectors = ['h2.sizen', 'h2.majyuu', 'h2.bussitu', 'h2.akuma', 
                                   'h2.doragon', 'h2.suraimu', 'h2.zonbi', 'h2.kami']
                    for alt_selector in all_selectors:
                        name_element = monster_soup.select_one(alt_selector)
                        if name_element:
                            break
                
                # それでも見つからない場合は一般的なh2タグを使用
                if not name_element:
                    h2_elements = monster_soup.find_all('h2')
                    # モンスター名らしいh2を探す（最初の文字列h2を使用）
                    for h2 in h2_elements:
                        text = h2.text.strip()
                        if text and len(text) < 50:  # 長すぎるテキストは除外
                            name_element = h2
                            break
                
                if not name_element:
                    print(f"    警告: モンスター名が見つかりません ({system_name}): {monster_url}")
                    continue  # モンスター名が見つからない場合はスキップ
                name = name_element.text.strip()
                print(f"    処理中: {name}")
                
                # 特性・耐性・スキル情報を初期化
                tokusei = []
                taisei = {}
                skills = []
                    
                
                # 全てのテーブルから特性・耐性情報を探す
                tables = monster_soup.find_all('table')
                for table in tables:
                    text = table.get_text()
                    # 特性と耐性の情報が含まれているテーブルを探す
                    if '特性' in text and '耐性' in text:
                        # テーブルの行を処理
                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 3:
                                # 1列目が特性、2列目が耐性、3列目が出現場所
                                tokusei_cell = cells[0]
                                taisei_cell = cells[1]
                                
                                # 特性の処理
                                tokusei_text = tokusei_cell.get_text().strip()
                                if tokusei_text and tokusei_text != '特性':
                                    # 改行で分割して複数の特性を取得
                                    tokusei_list = [t.strip() for t in tokusei_text.split('\n') if t.strip()]
                                    tokusei.extend(tokusei_list)
                                
                                # 耐性の処理（色分け情報も含める）
                                if taisei_cell and taisei_cell.get_text().strip() != '耐性':
                                    # HTMLを解析して色分け情報を処理
                                    taisei_lines = []
                                    
                                    # br タグで分割された各行を処理
                                    content = str(taisei_cell)
                                    lines = content.split('<br/>')
                                    
                                    for line in lines:
                                        # HTMLタグを含む行をBeautifulSoupで解析
                                        line_soup = BeautifulSoup(line, 'html.parser')
                                        
                                        # spanタグがある場合の処理
                                        purple_spans = line_soup.find_all('span', class_='c-purple2')
                                        red_spans = line_soup.find_all('span', class_='c-red2')
                                        
                                        if purple_spans:
                                            for span in purple_spans:
                                                span_text = span.get_text().strip()
                                                if span_text:
                                                    taisei_lines.append(f"{span_text}（強の場合）")
                                        elif red_spans:
                                            for span in red_spans:
                                                span_text = span.get_text().strip()
                                                if span_text:
                                                    taisei_lines.append(f"{span_text}（最強の場合）")
                                        else:
                                            # 通常のテキスト
                                            plain_text = line_soup.get_text().strip()
                                            if plain_text:
                                                taisei_lines.append(plain_text)
                                    
                                    if taisei_lines:
                                        taisei['説明'] = '\n'.join(taisei_lines)
                        break
                
                # スキル情報を取得
                for table in tables:
                    text = table.get_text()
                    # スキルテーブルを特定（スキル名、特技、SPが含まれる）
                    if 'スキル' in text and '特技' in text and 'SP' in text:
                        rows = table.find_all('tr')
                        current_skill = None
                        
                        for row in rows[1:]:  # ヘッダー行をスキップ
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 5:
                                skill_name_cell = cells[0].get_text().strip()
                                technique_name = cells[2].get_text().strip()
                                sp_value = cells[3].get_text().strip()
                                effect = cells[4].get_text().strip()
                                
                                # 新しいスキルの開始
                                if skill_name_cell:
                                    current_skill = {
                                        'スキル名': skill_name_cell,
                                        '特技': []
                                    }
                                    skills.append(current_skill)
                                
                                # 特技情報を追加
                                if current_skill and technique_name:
                                    technique_info = {
                                        '技名': technique_name,
                                        'SP': sp_value,
                                        '効果': effect
                                    }
                                    current_skill['特技'].append(technique_info)
                        break

                # モンスターデータに系統情報も追加
                all_monsters_data[name] = {
                    "系統": system_name,
                    "特性": tokusei, 
                    "耐性": taisei, 
                    "スキル": skills
                }
                
            except requests.RequestException:
                print(f"    ネットワークエラー: {monster_url}")
                continue # 個別ページの取得失敗はスキップ
            except Exception as e:
                print(f"    処理エラー: {monster_url} - {e}")
                continue

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_monsters_data, f, ensure_ascii=False, indent=4)
        
        print(f"データ取得完了！総モンスター数: {len(all_monsters_data)}")
        return all_monsters_data

    except requests.RequestException as e:
        return {"error": f"ネットワークエラー: {e}"}
    except Exception as e:
        return {"error": f"予期せぬエラーが発生しました: {e}"}


def main():
    """メイン関数：スクレイピングを実行してJSONファイルに保存"""
    print("=== DQMJ2 モンスターデータスクレイピング開始 ===")
    
    result = scrape_monster_data()
    
    if "error" in result:
        print(f"❌ エラーが発生しました: {result['error']}")
        return False
    else:
        print(f"✅ 成功！{len(result)}体のモンスターデータを{DATA_FILE}に保存しました。")
        
        # 系統別集計を表示
        system_count = {}
        for name, data in result.items():
            system = data.get('系統', '未知')
            system_count[system] = system_count.get(system, 0) + 1
        
        print("\n=== 系統別集計 ===")
        for system, count in sorted(system_count.items()):
            print(f"  {system}: {count}体")
        
        return True


if __name__ == "__main__":
    main()
