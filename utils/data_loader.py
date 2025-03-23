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
    member.csv からメンバー情報を読み込んで、グループごとに格納する
    CSVの形式:
    15min,1hour,name,league
    
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
    
    try:
        # CSVファイルを直接読み込む
        with open('members.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # ヘッダー行をスキップ (最初の行)
        for line in lines[1:]:
            if not line.strip():
                continue
                
            # カンマで分割
            parts = line.strip().split(',')
            
            # U17メンバーの検出
            if "U17" in line:
                # U17の形式: normal_url,,name,U17
                if len(parts) >= 4:
                    normal_url = parts[0]
                    name = parts[2]
                    league = "U17"
                    final_url = None
                else:
                    print(f"U17メンバーのデータが不正: {line}")
                    continue
            else:
                # 通常メンバーの形式: final_url,normal_url,name,league
                if len(parts) >= 4:
                    final_url = parts[0] if parts[0].strip() else None
                    normal_url = parts[1] if parts[1].strip() else None
                    name = parts[2]
                    league = parts[3]
                else:
                    print(f"通常メンバーのデータが不正: {line}")
                    continue
            
            # メンバー情報を作成
            member_info = {
                "normal_url": normal_url,
                "final_url": final_url,
                "name": name
            }
            
            # リーグごとのリストに追加
            if league in member_groups:
                member_groups[league].append(member_info)
                member_groups["すべて"].append(member_info)
        
        return member_groups
    
    except Exception as e:
        print(f"member.csvの読み込み中にエラーが発生しました: {e}")
        # エラー時は空の辞書を返す
        return {key: [] for key in member_groups.keys()}


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