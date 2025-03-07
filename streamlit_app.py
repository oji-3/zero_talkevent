import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from io import StringIO
from datetime import datetime
import pytz

# ページの設定
st.set_page_config(
    page_title="完売表",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# カスタムCSS
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .inventory-matrix {
        margin-top: 20px;
    }
    .matrix-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .member-name {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .time-slot {
        font-size: 12px;
        text-align: center;
        padding: 8px 4px;
        white-space: nowrap;
    }
    .status-icon {
        font-size: 20px;
        font-weight: bold;
        text-align: center;
    }
    .sold-out {
        color: #dc3545;
    }
    .last-one {
        color: #198754;
    }
    .crowded {
        color: #fd7e14;
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    .header h1 {
        color: #212529;
        font-weight: 700;
    }
    .filter-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .update-time {
        color: #6c757d;
        font-size: 14px;
        text-align: right;
        margin-bottom: 10px;
    }
    .time-header {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        transform: rotate(180deg);
        height: 80px;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        padding: 8px 0px;
    }
    /* 枠の完売数ラベルのスタイル */
    .sold-out-count {
        display: block;
        font-size: 11px;
        font-weight: bold;
        background-color: #dc3545;
        color: white;
        padding: 2px 4px;
        border-radius: 4px;
        margin-bottom: 4px;
        text-align: center;
    }
    /* オレンジ文字(混雑時間帯)を黒文字と同じ方向にする */
    .crowded-label {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        transform: rotate(180deg);
        display: inline;
        color: #fd7e14;
        font-weight: bold;
    }
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    th {
        background-color: #f2f2f2;
        position: sticky;
        top: 0;
        z-index: 1;
    }
    th:first-child {
        position: sticky;
        left: 0;
        z-index: 2;
        background-color: #f2f2f2;
    }
    td:first-child {
        position: sticky;
        left: 0;
        background-color: #f2f2f2;
        font-weight: bold;
        z-index: 1;
    }
    .time-container {
        max-height: 80vh;
        overflow-x: auto;
        overflow-y: auto;
    }
    .group-filter {
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
        margin-bottom: 20px;
        background-color: #f1f3f5;
        width: auto;         /* 自動幅 */
        min-width: 250px;    /* 必要に応じて最小幅を設定 */
        max-width: 400px; 
    }
    .filter-label {
        font-weight: 600;
        margin-bottom: 5px;
        font-size: 14px;
        color: #212529;
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 13px;
        white-space: normal;   /* 複数行にしたい場合 */
        overflow: visible;     /* テキストを切り捨てない */
        text-overflow: clip;   /* 必要に応じて ellipsis をやめる */
        line-height: 1.5;   /* 行間を広めにとる */
        padding: 4px 8px;   /* 上下・左右に余白をつける */
    }
    /* プルダウンのテキストサイズを調整 */
    .stSelectbox div[data-baseweb="select"] span {
        font-size: 13px !important;
    }
    /* ドロップダウンメニューのテキストサイズを調整 */
    .stSelectbox ul li {
        font-size: 13px !important;
    }
    /* メンバー名のリンクのスタイル */
    .member-link {
        color: #212529;
        text-decoration: none;
        cursor: pointer;
    }
    .member-link:hover {
        color: #0d6efd;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# 日本時間のタイムゾーン設定
jst = pytz.timezone('Asia/Tokyo')

# アプリのヘッダー
st.markdown('<div class="header"><h1>完売表</h1></div>', unsafe_allow_html=True)

def parse_member_groups():
    """
    member.txt からメンバー情報を読み込んで、グループごとに格納する
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
            parts = line.split(',', 1)
            if len(parts) == 2:
                url, member_name = parts
                member_info = {"url": url, "name": member_name}
                member_groups[current_group].append(member_info)
                member_groups["すべて"].append(member_info)
    
    return member_groups

# 在庫状況を取得する関数
async def get_inventory_status(url, session):
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
        st.error(f"エラーが発生しました: {e}")
        return {}

# 並列処理で在庫状況を取得
async def get_inventory_with_progress(urls, member_names, progress_bar, status_text):
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

# セッション状態の初期化関数
def initialize_session_state():
    if 'inventory_data_all' not in st.session_state:
        st.session_state.inventory_data_all = {}
        st.session_state.data_loaded = False
        st.session_state.all_time_slots = set()
        st.session_state.last_update_time = None
        # メンバーURLを格納する辞書を初期化
        st.session_state.member_urls = {}

# 時間帯が15:00-15:15から17:45-18:00の範囲かどうかをチェックする関数
def is_early_time_slot(time_slot):
    early_slots = [
        "15:00-15:15", "15:15-15:30", "15:30-15:45", "15:45-16:00",
        "16:00-16:15", "16:15-16:30", "16:30-16:45", "16:45-17:00",
        "17:00-17:15", "17:15-17:30", "17:30-17:45", "17:45-18:00"
    ]
    return time_slot in early_slots

# 時間帯が18:00-18:15から21:45-22:00の範囲かどうかをチェックする関数
def is_regular_time_slot(time_slot):
    # 18:00-18:15から21:45-22:00までの時間帯
    return time_slot.startswith(("18:", "19:", "20:", "21:"))

def main():
    # セッション状態の初期化
    initialize_session_state()
    
    # メンバーグループデータを取得 (member.txt から)
    member_groups = parse_member_groups()
    
    # メンバー名とURLの辞書を作成
    member_urls = {}
    for member_list in member_groups.values():
        for member in member_list:
            member_urls[member["name"]] = member["url"]
    
    # セッション状態に保存
    st.session_state.member_urls = member_urls
    
    # 進捗状況表示用のプレースホルダー
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # 最初のロード時のみデータを取得
    if not st.session_state.data_loaded:
        progress_bar = progress_placeholder.progress(0)
        status_text = status_placeholder.empty()
        
        # すべてのメンバーのURLとメンバー名を取得
        all_members = member_groups["すべて"]
        urls = [member["url"] for member in all_members]
        member_names = [member["name"] for member in all_members]
        
        # 非同期処理で在庫状況を取得（進捗表示付き）
        inventory_data = asyncio.run(get_inventory_with_progress(urls, member_names, progress_bar, status_text))
        
        # セッション状態に保存
        st.session_state.inventory_data_all = inventory_data
        
        # 全ての時間帯を収集してセッション状態に保存
        all_time_slots = set()
        for member_data in inventory_data.values():
            all_time_slots.update(member_data.keys())
        st.session_state.all_time_slots = all_time_slots
        
        # 最終更新時間を保存
        st.session_state.last_update_time = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.data_loaded = True
        
        # 少し待機してから進捗表示を消す
        time.sleep(1)
        progress_placeholder.empty()
        status_placeholder.empty()
    
    # フィルターUI
    st.markdown('<div class="filter-label">リーグで絞り込む:</div>', unsafe_allow_html=True)
    selected_group = st.selectbox(
        label="リーグ選択",
        options=list(member_groups.keys()),
        index=0,
        label_visibility="collapsed",
        key="group_filter"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 選択されたグループに基づいてメンバーリストをフィルタリング
    filtered_members = member_groups[selected_group]
    
    if filtered_members:
        # 更新時間を表示
        st.markdown(f'<div class="update-time">最終更新: {st.session_state.last_update_time}</div>', unsafe_allow_html=True)
        st.markdown("""
<div class="footnote">
    <span style="color: orange; font-weight: bold;">オレンジ</span> : 混雑(15人以上)
</div>""", unsafe_allow_html=True)
        
        # 時間帯をソート
        def parse_time_range(time_range):
            # "15:00-15:15" 形式の時間帯から開始時間を取得してソート
            if '-' in time_range:
                start_time = time_range.split('-')[0].strip()
                if ':' in start_time:
                    hours, minutes = map(int, start_time.split(':'))
                    return hours * 60 + minutes
            return 0
        
        sorted_time_slots = sorted(list(st.session_state.all_time_slots), key=parse_time_range)
        
        # マトリクス表を作成
        st.markdown('<div class="time-container">', unsafe_allow_html=True)
        
        # HTMLテーブルの作成
        table_html = "<table>"
        
        # フィルター用のメンバー名リスト
        filtered_member_names = [member["name"] for member in filtered_members]
        
        # フィルタリングされたインベントリデータ
        filtered_inventory_data = {
            name: st.session_state.inventory_data_all.get(name, {}) 
            for name in filtered_member_names
        }
        
        # 特殊制御のための「18:00-18:15」〜「21:45-22:00」までの枠をすべて売った人のカウント
        members_sold_all_regular_slots = 0
        
        # すべてのメンバーに対して「18:00-18:15」〜「21:45-22:00」の枠をすべて売ったかチェック
        for m_name, m_data in st.session_state.inventory_data_all.items():
            # 各メンバーの「18:00-18:15」〜「21:45-22:00」の枠をチェック
            all_regular_slots_sold = True
            
            # 18時以降の枠が存在するかチェック
            has_regular_slots = False
            
            for time_slot in sorted_time_slots:
                if is_regular_time_slot(time_slot):
                    has_regular_slots = True
                    # この時間帯のデータがないか、売り切れではない場合
                    if time_slot not in m_data or m_data[time_slot] != "×":
                        all_regular_slots_sold = False
                        break
            
            # 18時以降の枠がすべて売り切れならカウント
            if has_regular_slots and all_regular_slots_sold:
                members_sold_all_regular_slots += 1

        # メンバー名からグループを取得するための辞書を作成
        member_groups_map = {}
        for group_name, members in member_groups.items():
            if group_name != "すべて":  # "すべて"は実際のグループではないのでスキップ
                for member in members:
                    member_groups_map[member["name"]] = group_name

        # 時間帯ごとの完売数をカウント
        sold_out_counts = {}
        for time_slot in sorted_time_slots:
            # 各時間帯の完売数をカウント
            slot_sold_out_count = 0
            
            # 15:00-18:00の時間帯は特殊な判定
            if is_early_time_slot(time_slot):
                # 15:00-18:00の時間帯は「18時以降全て完売」かつ「その枠が×」のメンバーをカウント
                for m_name, m_data in st.session_state.inventory_data_all.items():
                    # U17グループのメンバーは特殊判定から除外
                    is_u17_member = member_groups_map.get(m_name) == "U17"
                    
                    if is_u17_member:
                        # U17メンバーは通常のカウント（15:00-18:00も普通に×ならカウント）
                        if time_slot in m_data and m_data[time_slot] == "×":
                            slot_sold_out_count += 1
                    else:
                        # U17以外のメンバーは特殊判定
                        # 18時以降の全ての枠が完売しているかチェック
                        all_regular_slots_sold = True
                        has_regular_slots = False
                        
                        for reg_time_slot in sorted_time_slots:
                            if is_regular_time_slot(reg_time_slot):
                                has_regular_slots = True
                                if reg_time_slot not in m_data or m_data[reg_time_slot] != "×":
                                    all_regular_slots_sold = False
                                    break
                        
                        # 18時以降の枠が全て完売していて、かつこの時間帯も×の場合のみカウント
                        if has_regular_slots and all_regular_slots_sold and time_slot in m_data and m_data[time_slot] == "×":
                            slot_sold_out_count += 1
            else:
                # 18:00以降の時間帯は通常の判定
                for m_name, m_data in st.session_state.inventory_data_all.items():
                    if time_slot in m_data and m_data[time_slot] == "×":
                        slot_sold_out_count += 1
            
            sold_out_counts[time_slot] = slot_sold_out_count

        # 混雑時間帯の判定
        crowded_time_slots = {}
        for time_slot in sorted_time_slots:
            if is_early_time_slot(time_slot):
                # 「15:00-15:15」〜「17:45-18:00」は特殊条件
                crowded_time_slots[time_slot] = (members_sold_all_regular_slots >= 15)
            else:
                # 通常の混雑判定: 15人以上が売り切れの場合は混雑マーク
                crowded_time_slots[time_slot] = (sold_out_counts[time_slot] >= 15)

        # ヘッダー行
        table_html += "<tr><th>メンバー名</th>"

        # 時間帯ヘッダーを表示
        for time_slot in sorted_time_slots:
            header_class = "time-header"
            if crowded_time_slots[time_slot]:
                header_class += " crowded"
                # オレンジ文字（縦向き、黒文字と同じ向き）
                time_slot_display = f'<span class="crowded-label">{time_slot}</span>'
            else:
                time_slot_display = time_slot
            
            # 完売数ラベルを追加
            sold_out_count = sold_out_counts[time_slot]
            table_html += f'<th class="{header_class}"><span class="sold-out-count">{sold_out_count}</span>{time_slot_display}</th>'
        
        table_html += "</tr>"
        
        # データ行
        for member_name in filtered_member_names:
            member_url = st.session_state.member_urls.get(member_name, "#")
            
            # リンク付きメンバー名のセル
            table_html += f'<tr><td><a href="{member_url}" target="_blank" class="member-link">{member_name}</a></td>'
            
            member_data = st.session_state.inventory_data_all.get(member_name, {})
            for time_slot in sorted_time_slots:
                status = member_data.get(time_slot, "")
                status_class = "sold-out" if status == "×" else "last-one" if status == "⚪︎" else ""
                table_html += f'<td class="status-icon {status_class}">{status}</td>'
            
            table_html += "</tr>"
        
        table_html += "</table>"
        
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(f"選択されたリーグ '{selected_group}' にはメンバーがいません。")

if __name__ == "__main__":
    main()
