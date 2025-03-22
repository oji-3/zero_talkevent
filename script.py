from bs4 import BeautifulSoup
import re
import csv
import sys
import logging
import json
import os

# ログ設定: INFOレベル以上のログを、タイムスタンプ付きで出力する
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_member_info(html_content):
    """
    HTMLコンテンツからメンバーのURLと名前を抽出する関数
    """
    logging.info("HTML解析を開始します。")
    soup = BeautifulSoup(html_content, 'html.parser')
    members = []
    # a要素をすべて取得
    a_elements = soup.find_all('a', class_='items-grid_anchor_5c97110f js-anchor')
    logging.info(f"見つかったaタグの数: {len(a_elements)}")
    
    for idx, a_element in enumerate(a_elements, start=1):
        url = a_element.get('href')
        title_element = a_element.find('p', class_='items-grid_itemTitleText_5c97110f')
        if title_element:
            title_text = title_element.text
            # "【Z1-A】白咲 ひとみ トークイベント" から "白咲 ひとみ" を抽出
            match = re.search(r'】(.*?) トークイベント', title_text)
            if match:
                member_name = match.group(1)
                members.append((url, member_name))
                logging.info(f"{idx}番目のメンバー: {member_name} ({url}) を抽出しました。")
            else:
                logging.warning(f"{idx}番目のaタグでメンバー名抽出に失敗しました。テキスト: {title_text}")
        else:
            logging.warning(f"{idx}番目のaタグにタイトル要素が見つかりませんでした。")
    
    logging.info("HTML解析を完了しました。")
    return members

def save_to_csv(members, filename='member_urls.csv'):
    """
    メンバー情報をCSVファイルに保存する関数
    """
    logging.info(f"CSVファイル {filename} への保存を開始します。")
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'メンバー名'])
        writer.writerows(members)
    logging.info(f"{len(members)}人のメンバー情報を {filename} に保存しました。")

def save_to_json(members, filename='member_urls.json'):
    """
    メンバー情報をJSONファイルに保存する関数
    """
    logging.info(f"JSONファイル {filename} への保存を開始します。")
    # 辞書形式に変換
    member_dict = {member_name: url for url, member_name in members}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(member_dict, f, ensure_ascii=False, indent=2)
    logging.info(f"{len(members)}人のメンバー情報を {filename} に保存しました。")

def main():
    """
    メイン関数
    """
    logging.info("プログラムを開始します。")
    
    # コマンドライン引数でファイルパスが指定されているか確認
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # ファイルパスが指定されていない場合はユーザーに入力を求める
        input_filename = input("HTMLファイルのパスを入力してください: ")
    
    # ファイルの存在確認
    if not os.path.exists(input_filename):
        logging.error(f"指定されたファイル {input_filename} が見つかりません。")
        sys.exit(1)
    
    # ファイル読み込み
    logging.info(f"入力ファイル {input_filename} を読み込みます。")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        logging.info("HTMLコンテンツの読み込みが完了しました。")
    except Exception as e:
        logging.error(f"ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)
    
    # メンバー情報を抽出
    members = extract_member_info(html_content)
    logging.info(f"合計{len(members)}人のメンバーが見つかりました。")
    for url, name in members:
        logging.info(f"抽出されたメンバー: {name} - {url}")
    
    # CSVとJSONに保存
    save_to_csv(members)
    save_to_json(members)
    logging.info("プログラムの実行が完了しました。")

if __name__ == "__main__":
    main()