import csv
import re
from collections import defaultdict

def extract_member_info(title):
    """タイトルからメンバー名とグループ名を抽出"""
    # 【グループ名】メンバー名 トークイベント の形式から抽出
    match = re.match(r'【(.+?)】(.+?)\s+トークイベント', title)
    if match:
        group = match.group(1).strip()
        name = match.group(2).strip()
        return group, name
    return None, None

def main():
    # メンバー情報を格納する辞書とメンバーの順序を保持するリスト
    members = defaultdict(lambda: {'group': '', 'url_1hour': '', 'url_15min': ''})
    member_order = []
    
    # item.csvを読み込む (BOM対応)
    with open('item.csv', 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            title = row['title']
            url = row['url']
            
            # メンバー名とグループ名を抽出
            group, name = extract_member_info(title)
            if not group or not name:
                continue
            
            # 初回登場時に順序を記録
            if name not in members:
                member_order.append(name)
            
            # 鍵〆パックがあるかどうかで判定
            if '鍵〆' in title:
                # 1時間チケット
                members[name]['group'] = group
                members[name]['url_1hour'] = url
            else:
                # 15分チケット
                members[name]['group'] = group
                members[name]['url_15min'] = url
    
    # 1hourがないメンバーは15minのurlを両方に設定
    for name, info in members.items():
        if not info['url_1hour'] and info['url_15min']:
            info['url_1hour'] = info['url_15min']
    
    # members.csvに出力 (item.csvの順序を保持)
    with open('members.csv', 'w', encoding='utf-8', newline='') as file:
        fieldnames = ['url_1hour', 'url_15min', 'name', 'group']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for name in member_order:
            info = members[name]
            writer.writerow({
                'url_1hour': info['url_1hour'],
                'url_15min': info['url_15min'],
                'name': name,
                'group': info['group']
            })

if __name__ == '__main__':
    main()