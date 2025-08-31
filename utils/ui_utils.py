"""
UI表示やHTMLテーブル生成に関する関数
"""

def format_time_slot_display(time_slot):
    """
    時間枠の表示形式を「XX:XX-XX:XX」から「XX:XX」（開始時刻のみ）に変換
    
    Args:
        time_slot (str): 元の時間枠文字列（例: "15:00-15:15"）
        
    Returns:
        str: 開始時刻のみの文字列（例: "15:00"）
    """
    if '-' in time_slot:
        return time_slot.split('-')[0].strip()
    return time_slot

def generate_table_html(filtered_members, sorted_time_slots, inventory_data, member_urls, 
                        member_groups_map, sold_out_counts, crowded_time_slots, member_sales_count):
    """
    在庫情報を表示するHTMLテーブルを生成
    
    Args:
        filtered_members (list): フィルタリングされたメンバー情報リスト
        sorted_time_slots (list): ソートされた時間帯のリスト
        inventory_data (dict): メンバー名と在庫情報のマッピング
        member_urls (dict): メンバー名とURLのマップ
        member_groups_map (dict): メンバー名からグループを取得するマップ
        sold_out_counts (dict): 時間帯と完売数のマッピング
        crowded_time_slots (dict): 時間帯と混雑状態のマッピング
        member_sales_count (dict): メンバー名と売上数のマッピング
        
    Returns:
        str: 生成されたHTMLテーブル
    """
    from utils.data_loader import format_member_name
        
    # フィルター用のメンバー名リスト
    filtered_member_names = [member["name"] for member in filtered_members]
    
    # テーブルHTMLを生成
    html = """
    <div class="table-scroll-container">
        <table class="inventory-table">
    """
    
    # ヘッダー行
    html += "<thead><tr>"
    html += '<th class="corner-header">メンバー名</th>'
    
    # 時間帯ヘッダー
    for time_slot in sorted_time_slots:
        time_display = format_time_slot_display(time_slot)
        header_class = "time-header"
        
        if crowded_time_slots[time_slot]:
            header_class += " crowded"
            time_slot_display = f'<span class="crowded-label">{time_display}</span>'
        else:
            time_slot_display = time_display
        
        # 完売数ラベルを追加
        sold_out_count = sold_out_counts[time_slot]
        count_class = "sold-out-count crowded" if crowded_time_slots[time_slot] else "sold-out-count"
        
        html += f'<th class="{header_class}">'
        html += f'{time_slot_display}'
        html += f'<span class="{count_class}">{sold_out_count}</span>'
        html += '</th>'
    
    html += "</tr></thead>"
    
    # データ行
    html += "<tbody>"
    
    for member_name in filtered_member_names:
        # メンバーのURLを取得（通常枠と最終枠の両方）
        member_url_dict = member_urls.get(member_name, {})
        normal_url = member_url_dict.get("normal", "#")
        
        html += "<tr>"
        
        # メンバー名セル - 縦方向中央揃えのためのフレックスボックスコンテナを使用
        formatted_name = format_member_name(member_name)
        sales_count = member_sales_count[member_name]
        
        html += f'<td class="member-cell">'
        html += f'<div class="member-name-container">'
        html += f'<a href="{normal_url}" target="_blank" class="member-link">{formatted_name}</a>'
        html += f'<span class="member-sales-count">{sales_count}</span>'
        html += f'</div></td>'
        
        # メンバーの時間帯ごとの状態セル
        member_data = inventory_data.get(member_name, {})
        
        for time_slot in sorted_time_slots:
            status = member_data.get(time_slot, "")
            
            # ステータスの表示とクラス設定
            if status == "◎" or status == "⚪︎" or status == "○":
                display_status = "○"
                status_class = "last-one"
            elif status == "×":
                display_status = status
                status_class = "sold-out"
            elif status == "🔒":
                display_status = status
                status_class = "locked"
            else:
                display_status = status
                status_class = ""
            
            html += f'<td class="status-cell {status_class}">{display_status}</td>'
        
        html += "</tr>"
    
    html += "</tbody></table></div>"
    
    return html

def determine_crowded_time_slots(sorted_time_slots, sold_out_counts):
    """
    混雑時間帯を判定
    
    Args:
        sorted_time_slots (list): ソートされた時間帯のリスト
        sold_out_counts (dict): 時間帯と完売数のマッピング
        
    Returns:
        dict: 時間帯と混雑状態のマッピング
    """
    crowded_time_slots = {}
    for time_slot in sorted_time_slots:
        # 全時間帯で通常の混雑判定: 15人以上が売り切れの場合は混雑マーク
        crowded_time_slots[time_slot] = (sold_out_counts[time_slot] >= 15)
    
    return crowded_time_slots

