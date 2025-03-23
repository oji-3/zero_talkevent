"""
在庫情報の取得と処理を行うモジュール
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from utils.time_utils import is_early_time_slot, is_regular_time_slot, is_after_final_slot_deadline


async def get_inventory_status(url, session):
    """
    URLから在庫状況を取得する
    """
    try:
        if url is None:
            return {}
            
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                time_slots = {}
                variation_items = soup.select('.cot-itemOrder-variationLI')
                
                for item in variation_items:
                    time_slot = item.select_one('.cot-itemOrder-variationName')
                    
                    if time_slot:
                        time_text = time_slot.text.strip()
                        item_text = item.text.strip()
                        
                        # 販売開始通知希望の場合（15:00-18:00の時間帯）
                        if "販売開始通知希望" in item_text and time_text.startswith(("15:", "16:", "17:")):
                            status = "🔒"  # 鍵アイコン（未解放状態）
                        # 再入荷通知希望の場合は完売
                        elif "再入荷通知希望" in item_text or "販売開始通知希望" in item_text:
                            status = "×"  # 完売
                        else:
                            # 残り1点かどうかをチェック
                            stock_info = item.select_one('.cot-itemOrder-variationStock')
                            if stock_info and "残り1点" in stock_info.text.strip():
                                status = "⚪︎"  # 残りわずか
                            else:
                                status = "◎"  # 在庫あり
                        
                        time_slots[time_text] = status
                
                return time_slots
            return {}
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return {}
async def get_inventory_with_progress(member_urls, member_names, progress_bar, status_text):
    """
    並列処理で在庫状況を取得（通常枠と最終枠の両方）
    
    Args:
        member_urls (dict): メンバー名と通常枠/最終枠URLの辞書
        member_names (list): メンバー名のリスト
        progress_bar (streamlit.progress): 進捗バー
        status_text (streamlit.empty): 状態テキスト
        
    Returns:
        dict: メンバー名と在庫情報のマッピング
    """
    # 日本時間2025年3月25日23:59を過ぎているか確認
    use_final_slots = not is_after_final_slot_deadline()
    
    async with aiohttp.ClientSession() as session:
        # 通常枠と最終枠両方のURLリストを作成
        urls_to_fetch = []
        url_type_map = []  # URL種別のマッピング（通常枠か最終枠か）
        member_url_map = []  # どのメンバーのどの種別のURLか
        
        for member_name in member_names:
            member_url_dict = member_urls.get(member_name, {})
            # 通常枠URL
            normal_url = member_url_dict.get("normal")
            if normal_url:
                urls_to_fetch.append(normal_url)
                url_type_map.append("normal")
                member_url_map.append(member_name)
            
            # 最終枠URL（日付チェックに基づいて処理）
            if use_final_slots:
                final_url = member_url_dict.get("final")
                if final_url:
                    urls_to_fetch.append(final_url)
                    url_type_map.append("final")
                    member_url_map.append(member_name)
        
        total = len(urls_to_fetch)
        completed = 0
        results = []
        
        chunk_size = 55
        for i in range(0, total, chunk_size):
            chunk_urls = urls_to_fetch[i:i+chunk_size]
            
            # 進捗状況表示の更新
            status_text.info(f"在庫情報を取得中です... ({int(completed/total*100)}%)")

            # チャンク内のタスクを実行
            tasks = [get_inventory_status(url, session) for url in chunk_urls]
            chunk_results = await asyncio.gather(*tasks)
            results.extend(chunk_results)
            
            # 進捗を更新
            completed += len(chunk_urls)
            progress_bar.progress(completed / total)
            
            # サーバー負荷軽減のための待機
            await asyncio.sleep(0.1)  # 並列数を上げるので待機時間を少し短縮
        
        # 結果を辞書にまとめる
        inventory_data = {}
        final_slot_data = {}  # 最終枠の在庫情報を一時保存
        
        for i, result in enumerate(results):
            member_name = member_url_map[i]
            url_type = url_type_map[i]
            
            if url_type == "normal":
                # 通常枠のデータ
                if member_name not in inventory_data:
                    inventory_data[member_name] = result
            else:
                # 最終枠のデータ
                final_slot_data[member_name] = result
        
        # 日付チェックに基づいて最終枠の処理を行う
        if use_final_slots:
            # 通常枠の後ろ4枠を最終枠のデータで塗り替え
            for member_name, final_data in final_slot_data.items():
                # 最終枠の状態を確認
                final_sold_out = False
                has_final_data = False
                
                # 最終枠のデータがあれば、完売状態を確認
                if final_data:
                    has_final_data = True
                    # 最終枠のすべての時間帯が完売（×）かチェック
                    all_slots_sold_out = all(status == "×" for status in final_data.values())
                    # 少なくとも1つの時間帯が完売（×）かチェック
                    any_slot_sold_out = any(status == "×" for status in final_data.values())
                    
                    final_sold_out = all_slots_sold_out
                
                # 通常枠のデータがあれば、後ろ4枠を修正
                if member_name in inventory_data and has_final_data:
                    # 後ろ4枠の時間帯を特定（21:00以降）
                    normal_data = inventory_data[member_name]
                    
                    for time_slot in list(normal_data.keys()):
                        # 21:00以降の枠を特定
                        if time_slot.startswith("21:"):
                            if final_sold_out:
                                # 最終枠が完売していれば、×で上書き
                                normal_data[time_slot] = "×"
                            else:
                                # 最終枠が完売していなければ、◎で上書き
                                normal_data[time_slot] = "◎"
        
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