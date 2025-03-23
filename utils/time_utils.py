"""
時間帯の処理を行うユーティリティ関数
"""
from datetime import datetime
import pytz


def is_early_time_slot(time_slot):
    """
    時間帯が15:00-15:15から17:45-18:00の範囲かどうかをチェックする
    
    Args:
        time_slot (str): チェックする時間帯
        
    Returns:
        bool: 早い時間帯の場合はTrue
    """
    early_slots = [
        "15:00-15:15", "15:15-15:30", "15:30-15:45", "15:45-16:00",
        "16:00-16:15", "16:15-16:30", "16:30-16:45", "16:45-17:00",
        "17:00-17:15", "17:15-17:30", "17:30-17:45", "17:45-18:00"
    ]
    return time_slot in early_slots


def is_regular_time_slot(time_slot):
    """
    時間帯が18:00-18:15から21:45-22:00の範囲かどうかをチェックする
    
    Args:
        time_slot (str): チェックする時間帯
        
    Returns:
        bool: 通常時間帯の場合はTrue
    """
    # 18:00-18:15から21:45-22:00までの時間帯
    return time_slot.startswith(("18:", "19:", "20:", "21:"))


def is_all_regular_slots_sold_out(member_data, sorted_time_slots):
    """
    メンバーの18:00以降の枠が全て完売しているかチェック
    
    Args:
        member_data (dict): メンバーの時間帯ごとの在庫情報
        sorted_time_slots (list): ソートされた時間帯のリスト
        
    Returns:
        bool: 18:00以降の枠が全て完売している場合はTrue
    """
    all_regular_slots_sold = True
    has_regular_slots = False
    
    for time_slot in sorted_time_slots:
        if is_regular_time_slot(time_slot):
            has_regular_slots = True
            if time_slot not in member_data or member_data[time_slot] != "×":
                all_regular_slots_sold = False
                break
    
    return has_regular_slots and all_regular_slots_sold


def sort_time_slots(time_slots):
    """
    時間帯を開始時間でソートする
    
    Args:
        time_slots (set): 時間帯の集合
        
    Returns:
        list: ソートされた時間帯のリスト
    """
    def parse_time_range(time_range):
        # "15:00-15:15" 形式の時間帯から開始時間を取得してソート
        if '-' in time_range:
            start_time = time_range.split('-')[0].strip()
            if ':' in start_time:
                hours, minutes = map(int, start_time.split(':'))
                return hours * 60 + minutes
        return 0
    
    return sorted(list(time_slots), key=parse_time_range)


def is_after_final_slot_deadline():
    """
    現在の日時が日本時間2025年3月25日23:59を過ぎているかどうかをチェックする
    
    Returns:
        bool: 指定した日時を過ぎている場合はTrue
    """
    # 日本時間の現在時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    # 基準日時 (2025年3月25日23:59:59)
    deadline = datetime(2025, 3, 25, 23, 59, 59, tzinfo=jst)
    
    # 現在時刻が基準日時を過ぎているかチェック
    return now > deadline