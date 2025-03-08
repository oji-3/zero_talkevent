"""
在庫情報の取得と処理を行うモジュール
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def get_inventory_status(url, session):
    """
    URLから在庫状況を取得する
    
    Args:
        url (str): 在庫情報を取得するURL
        session (aiohttp.ClientSession): HTTPセッション
        
    Returns:
        dict: 時間帯と在庫状況のマッピング
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 時間帯ごとの在庫情報を取得
                time_slots = {}
                variation_items = soup.select('.cot-itemOrder-variationLI')
                
                for item in variation_items:
                    time_slot = item.select_one('.cot-itemOrder-variationName')
                    stock_info = item.select_one('.cot-itemOrder-variationStock')
                    
                    if time_slot and stock_info:
                        time_text = time_slot.text.strip()
                        stock_text = stock_info.text.strip()
                        
                        if "在庫なし" in stock_text:
                            status = "×"
                        elif "残り1点" in stock_text:
                            status = "⚪︎"
                        else:
                            status = "◎"  # その他の状態
                        
                        time_slots[time_text] = status
                
                return time_slots
            return {}  # エラー時は空の辞書を返す
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return {}


async def get_inventory_with_progress(urls, member_names, progress_bar, status_text):
    """
    並列処理で在庫状況を取得
    
    Args:
        urls (list): 在庫情報を取得するURLのリスト
        member_names (list): メンバー名のリスト
        progress_bar (streamlit.progress): 進捗バー
        status_text (streamlit.empty): 状態テキスト
        
    Returns:
        dict: メンバー名と在庫情報のマッピング
    """
    async with aiohttp.ClientSession() as session:
        total = len(urls)
        completed = 0
        results = []
        
        # タスクのチャンク作成（55並列）
        chunk_size = 55
        for i in range(0, total, chunk_size):
            chunk_urls = urls[i:i+chunk_size]
            chunk_members = member_names[i:i+chunk_size]
            
            # 進捗状況表示の更新
            status_text.info(f"在庫情報を取得中です... {completed}/{total} 完了 ({int(completed/total*100)}%)")
            
            # チャンク内のタスクを実行
            tasks = [get_inventory_status(url, session) for url in chunk_urls]
            chunk_results = await asyncio.gather(*tasks)
            results.extend(chunk_results)
            
            # 進捗を更新
            completed += len(chunk_urls)
            progress_bar.progress(completed / total)
            
            # サーバー負荷軽減のための待機
            await asyncio.sleep(0.2)  # 並列数を上げるので待機時間を少し短縮
        
        # 結果を辞書にまとめる
        inventory_data = {}
        for i, result in enumerate(results):
            if i < len(member_names):
                inventory_data[member_names[i]] = result
        
        # 完了表示
        status_text.success(f"在庫情報の取得が完了しました！ {total}/{total} 完了 (100%)")
        
        return inventory_data


def calculate_sold_out_counts(inventory_data, sorted_time_slots, member_groups_map, is_all_regular_slots_sold_out):
    """
    時間帯ごとの完売数をカウント
    
    Args:
        inventory_data (dict): メンバー名と在庫情報のマッピング
        sorted_time_slots (list): ソートされた時間帯のリスト
        member_groups_map (dict): メンバー名からグループを取得するマップ
        is_all_regular_slots_sold_out (function): 通常時間帯が全て完売しているかチェックする関数
        
    Returns:
        dict: 時間帯と完売数のマッピング
    """
    sold_out_counts = {}
    
    for time_slot in sorted_time_slots:
        # 各時間帯の完売数をカウント
        slot_sold_out_count = 0
        
        # 15:00-18:00の時間帯は特殊な判定
        if is_early_time_slot(time_slot):
            # 15:00-18:00の時間帯は「18時以降全て完売」かつ「その枠が×」のメンバーをカウント
            for m_name, m_data in inventory_data.items():
                # U17グループのメンバーは特殊判定から除外
                is_u17_member = member_groups_map.get(m_name) == "U17"
                
                if is_u17_member:
                    # U17メンバーは通常のカウント（15:00-18:00も普通に×ならカウント）
                    if time_slot in m_data and m_data[time_slot] == "×":
                        slot_sold_out_count += 1
                else:
                    # U17以外のメンバーは特殊判定
                    # 18時以降の枠が全て完売しているかチェック
                    if is_all_regular_slots_sold_out(m_data, sorted_time_slots) and time_slot in m_data and m_data[time_slot] == "×":
                        slot_sold_out_count += 1
        else:
            # 18:00以降の時間帯は通常の判定
            for m_name, m_data in inventory_data.items():
                if time_slot in m_data and m_data[time_slot] == "×":
                    slot_sold_out_count += 1
        
        sold_out_counts[time_slot] = slot_sold_out_count
    
    return sold_out_counts


def calculate_member_sales_count(member_names, inventory_data, sorted_time_slots, member_groups_map, is_all_regular_slots_sold_out, is_early_time_slot):
    """
    メンバーごとの売上数を計算
    
    Args:
        member_names (list): メンバー名のリスト
        inventory_data (dict): メンバー名と在庫情報のマッピング
        sorted_time_slots (list): ソートされた時間帯のリスト
        member_groups_map (dict): メンバー名からグループを取得するマップ
        is_all_regular_slots_sold_out (function): 通常時間帯が全て完売しているかチェックする関数
        is_early_time_slot (function): 早い時間帯かどうかをチェックする関数
        
    Returns:
        dict: メンバー名と売上数のマッピング
    """
    member_sales_count = {}
    
    for member_name in member_names:
        member_data = inventory_data.get(member_name, {})
        member_group = member_groups_map.get(member_name, "")
        is_u17_member = (member_group == "U17")
        sold_count = 0
        
        # 18時以降の枠が全て完売しているかを確認
        all_regular_slots_sold = is_all_regular_slots_sold_out(member_data, sorted_time_slots)
        
        # 各時間枠をチェック
        for time_slot, status in member_data.items():
            # 非U17メンバーの15:00-18:00の枠で、18:00以降が全て完売していない場合は未解放枠
            if not is_u17_member and is_early_time_slot(time_slot) and status == "×" and not all_regular_slots_sold:
                # 未解放枠はカウントしない
                continue
            elif status == "×":
                # それ以外の完売枠はカウント
                sold_count += 1
                
        member_sales_count[member_name] = sold_count
    
    return member_sales_count

# 時間ユーティリティの関数をimport
from utils.time_utils import is_early_time_slot