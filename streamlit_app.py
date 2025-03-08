import streamlit as st
import asyncio
import time
from datetime import datetime
import pytz

from styles.styles import load_css
from utils.data_loader import parse_member_groups, create_member_url_map, create_member_group_map
from utils.time_utils import is_early_time_slot, is_regular_time_slot, is_all_regular_slots_sold_out, sort_time_slots
from utils.inventory import get_inventory_with_progress, calculate_sold_out_counts, calculate_member_sales_count
from utils.ui_utils import generate_table_html, determine_crowded_time_slots, count_members_sold_all_regular_slots

# ページの設定
st.set_page_config(
    page_title="完売表",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# カスタムCSSを適用
st.markdown(load_css(), unsafe_allow_html=True)

# 日本時間のタイムゾーン設定
jst = pytz.timezone('Asia/Tokyo')

# アプリのヘッダー
st.markdown('<div class="header"><h1>完売表</h1></div>', unsafe_allow_html=True)

# セッション状態の初期化関数
def initialize_session_state():
    """
    セッション状態を初期化する
    """
    if 'inventory_data_all' not in st.session_state:
        st.session_state.inventory_data_all = {}
        st.session_state.data_loaded = False
        st.session_state.all_time_slots = set()
        st.session_state.last_update_time = None
        # メンバーURLを格納する辞書を初期化
        st.session_state.member_urls = {}

def main():
    """
    アプリケーションのメイン関数
    """
    # セッション状態の初期化
    initialize_session_state()
    
    # メンバーグループデータを取得 (member.txt から)
    member_groups = parse_member_groups()
    
    # メンバー名とURLの辞書を作成
    member_urls = create_member_url_map(member_groups)
    
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
        
        # 時間帯をソート
        sorted_time_slots = sort_time_slots(st.session_state.all_time_slots)
        
        # マトリクス表を作成
        st.markdown('<div class="time-container">', unsafe_allow_html=True)
        
        # 凡例の表示
        st.markdown("""
        <div class="footnote" style="margin-bottom: 15px;">
            <span class="legend-item"><span style="color: #fd7e14; font-weight: bold;">オレンジ</span> : 混雑(15人以上)</span>
        </div>""", unsafe_allow_html=True)
        
        # フィルター用のメンバー名リスト
        filtered_member_names = [member["name"] for member in filtered_members]
        
        # フィルタリングされたインベントリデータ
        filtered_inventory_data = {
            name: st.session_state.inventory_data_all.get(name, {}) 
            for name in filtered_member_names
        }
        
        # メンバー名からグループを取得するための辞書を作成
        member_groups_map = create_member_group_map(member_groups)
        
        # 特殊制御のための「18:00-18:15」〜「21:45-22:00」までの枠をすべて売った人のカウント
        members_sold_all_regular_slots = count_members_sold_all_regular_slots(
            st.session_state.inventory_data_all, 
            sorted_time_slots, 
            is_all_regular_slots_sold_out
        )

        # 時間帯ごとの完売数をカウント
        sold_out_counts = calculate_sold_out_counts(
            st.session_state.inventory_data_all, 
            sorted_time_slots, 
            member_groups_map, 
            is_all_regular_slots_sold_out
        )

        # 混雑時間帯の判定
        crowded_time_slots = determine_crowded_time_slots(
            sorted_time_slots, 
            sold_out_counts, 
            members_sold_all_regular_slots
        )

        # メンバーごとの売上数を計算
        member_sales_count = calculate_member_sales_count(
            filtered_member_names, 
            st.session_state.inventory_data_all, 
            sorted_time_slots, 
            member_groups_map,
            is_all_regular_slots_sold_out, 
            is_early_time_slot
        )

        # HTMLテーブルを生成して表示
        table_html = generate_table_html(
            filtered_members, 
            sorted_time_slots,
            st.session_state.inventory_data_all, 
            st.session_state.member_urls, 
            member_groups_map, 
            sold_out_counts, 
            crowded_time_slots, 
            member_sales_count
        )
        
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(f"選択されたリーグ '{selected_group}' にはメンバーがいません。")

if __name__ == "__main__":
    main()