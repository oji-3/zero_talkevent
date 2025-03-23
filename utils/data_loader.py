"""
メンバーデータの読み込みと処理を行うモジュール
"""
import re


def format_member_name(name):
    """
    メンバー名を自動的に改行して表示しやすくする
    特に長いメンバー名や、半角・全角の混在する名前に対応
    
    Args:
        name (str): フォーマットするメンバー名
        
    Returns:
        str: HTML改行タグ付きの整形済みメンバー名
    """
    # 名前にスペースがある場合はそこで分割
    if ' ' in name:
        return name.replace(' ', '<br>')
    
    # 日本語の姓名が明確に分かれている場合（例：苗字 名前）
    if '　' in name:  # 全角スペースで分割
        return name.replace('　', '<br>')
    
    # 漢字とカタカナ/ひらがなの境目で分割（例：三崎桃果 → 三崎<br>桃果）
    match = re.search(r'([一-龯々]+)([ぁ-んァ-ヶ]+)', name)
    if match:
        return f"{match.group(1)}<br>{match.group(2)}"
    
    # 姓と名が分からない場合で、名前が長い場合は適当な位置で改行
    if len(name) > 4:
        mid = len(name) // 2
        return f"{name[:mid]}<br>{name[mid:]}"
    
    return name


def parse_member_groups():
    """
    member.txt からメンバー情報を読み込んで、グループごとに格納する
    
    Returns:
        dict: グループ名をキー、メンバー情報リストを値とする辞書
    """
    # グループ構造の初期化
    member_groups = {
        "すべて": [],
        "Z1": [],
        "Z2": [],
        "Z3": [],
        "Z4": [],
        "Z5": [],
        "U17": []
    }
    
    # member.txtからデータを読み込む
    with open('member.txt', 'r', encoding='utf-8') as f:
        paste_data = f.read()

    lines = paste_data.strip().split('\n')
    current_group = None
    
    for line in lines:
        line = line.strip()
        if line in ["Z1", "Z2", "Z3", "Z4", "Z5", "U17"]:
            current_group = line
        elif line and current_group:
            parts = line.split(',')
            if current_group == "U17" and len(parts) == 2:
                # U17は通常枠URLのみ
                normal_url, member_name = parts
                member_info = {
                    "normal_url": normal_url, 
                    "final_url": None,  # U17は最終枠なし
                    "name": member_name
                }
                member_groups[current_group].append(member_info)
                member_groups["すべて"].append(member_info)
            elif len(parts) == 3:
                # Z1-Z5は通常枠URLと最終枠URLがある
                normal_url, final_url, member_name = parts
                member_info = {
                    "normal_url": normal_url, 
                    "final_url": final_url, 
                    "name": member_name
                }
                member_groups[current_group].append(member_info)
                member_groups["すべて"].append(member_info)
    
    return member_groups


def create_member_url_map(member_groups):
    """
    メンバー名とURL（通常枠と最終枠）の辞書を作成
    
    Args:
        member_groups (dict): グループごとのメンバー情報
        
    Returns:
        dict: メンバー名をキー、URLの辞書を値とする辞書
    """
    member_urls = {}
    for member_list in member_groups.values():
        for member in member_list:
            member_urls[member["name"]] = {
                "normal": member["normal_url"],
                "final": member["final_url"]
            }
    
    return member_urls


def create_member_group_map(member_groups):
    """
    メンバー名からグループを取得するための辞書を作成
    
    Args:
        member_groups (dict): グループごとのメンバー情報
        
    Returns:
        dict: メンバー名をキー、グループ名を値とする辞書
    """
    member_groups_map = {}
    for group_name, members in member_groups.items():
        if group_name != "すべて":  # "すべて"は実際のグループではないのでスキップ
            for member in members:
                member_groups_map[member["name"]] = group_name
    
    return member_groups_map