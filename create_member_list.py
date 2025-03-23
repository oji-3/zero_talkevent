from bs4 import BeautifulSoup
import re
import csv
import sys
import logging
import os

# ログ設定: INFOレベル以上のログを、タイムスタンプ付きで出力する
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_member_info(html_content):
    """
    HTMLコンテンツからメンバーのURL、名前、コードを抽出する関数
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
            # "【Z1-A】白咲 ひとみ トークイベント" や "【U17】名前 トークイベント" からコードと名前を抽出
            match = re.search(r'【([ZU]\d+)[-A-Z]*】(.*?) トークイベント', title_text)
            if match:
                member_code = match.group(1)  # Z1などのコード部分
                member_name = match.group(2)  # 名前部分
                members.append((url, member_name, member_code))
                logging.info(f"{idx}番目のメンバー: {member_name} ({member_code}) - {url} を抽出しました。")
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
        writer.writerow(['URL', 'メンバー名', 'コード'])
        writer.writerows(members)
    logging.info(f"{len(members)}人のメンバー情報を {filename} に保存しました。")

def merge_duplicates(input_file, output_file='members.csv'):
    """
    メンバー名が重複している行を統合する関数
    最初のURLを1列目（URL列）、2番目のURLを2列目（1hour列）として出力する
    """
    logging.info(f"入力ファイル {input_file} を処理します。")
    
    # メンバー名をキーとした辞書を作成
    member_dict = {}
    
    # 入力CSVファイルを読み込む
    try:
        with open(input_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)  # ヘッダー行をスキップ
            logging.info(f"入力CSVのヘッダー: {headers}")
            
            for row in reader:
                if len(row) >= 3:
                    url = row[0]
                    name = row[1]
                    code = row[2]
                    
                    # すでに同じ名前があれば2番目のURLとして追加
                    if name in member_dict:
                        member_dict[name]['second_url'] = url
                        logging.info(f"重複メンバー検出: {name} - 2番目のURL: {url}")
                    else:
                        # 新規メンバーの場合はエントリ作成
                        member_dict[name] = {
                            'first_url': url,
                            'second_url': '',  # 初期値は空文字列
                            'code': code
                        }
                        logging.info(f"新規メンバー追加: {name} - 1番目のURL: {url}")
                else:
                    logging.warning(f"不正な行フォーマット: {row}")
    except Exception as e:
        logging.error(f"入力ファイルの読み込みに失敗しました: {e}")
        sys.exit(1)
    
    # 出力CSVファイルに書き込む（※ヘッダーと行の順序を変更）
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # ヘッダー：1列目にURL（最初のURL）、2列目に1hour（2番目のURL）、3列目に名前、4列目にリーグコード
            writer.writerow(['15min', '1hour', 'name', 'league'])
            
            # 辞書からデータを取り出して書き込む
            for name, data in member_dict.items():
                # 重複がない場合、2番目のURLは空文字列となる
                second_url = data['second_url'] if data['second_url'] else ""
                row = [data['first_url'], second_url, name, data['code']]
                writer.writerow(row)
                
        logging.info(f"出力ファイル {output_file} へ {len(member_dict)} 人分のデータを書き込みました。")
    except Exception as e:
        logging.error(f"出力ファイルの書き込みに失敗しました: {e}")
        sys.exit(1)

def main():
    """
    メイン関数
    """
    logging.info("プログラムを開始します。")
    
    # コマンドライン引数でHTMLファイルが指定されているか確認
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
    
    # 一時CSVに保存
    temp_csv = 'member_urls.csv'
    save_to_csv(members, temp_csv)
    logging.info(f"メンバー情報を一時ファイル {temp_csv} に保存しました。")
    
    # 重複を統合して新しいCSVを作成
    output_csv = 'members.csv'
    merge_duplicates(temp_csv, output_csv)
    logging.info(f"重複メンバーを統合して {output_csv} に保存しました。")
    
    # 一時ファイルを削除
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        logging.info(f"一時ファイル {temp_csv} を削除しました。")
    
    logging.info("プログラムの実行が完了しました。")

if __name__ == "__main__":
    main()