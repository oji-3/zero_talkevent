def load_css():
    """
    アプリケーションのCSSスタイルを返す
    """
    return """
<style>
    /* テーブルコンテナの設定 */
    .time-container, .table-scroll-container {
        position: relative;
        overflow: auto;
        max-height: 80vh;
        max-width: 100%;
    }
    
    /* テーブル基本設定 */
    table, .inventory-table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        border: 1px solid #ddd;
    }
    
    /* セルの基本スタイル */
    th, td, .inventory-table th, .inventory-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        background-color: white;
    }
    
    /* ヘッダーセル (時間枠) */
    thead th, .time-header {
        background-color: #f2f2f2 !important;
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        top: 0;
        z-index: 10;
        min-width: 65px;
        text-align: center;
    }
    
    /* 最初の列 (メンバー名) */
    tbody td:first-child, .member-cell {
        background-color: #f2f2f2 !important;
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        left: 0;
        z-index: 1;
        text-align: left;
        min-width: 120px;
        max-width: 120px;
        padding: 0 8px; /* 内側のパディングを調整 */
        height: 64px; /* 高さを固定 */
    }
    
    /* メンバー名のコンテナ - 縦方向中央揃え */
    .member-name-container {
        display: flex;
        align-items: center; /* 垂直方向中央揃え */
        justify-content: space-between; /* 名前と数字を左右に配置 */
        height: 100%;
        width: 100%;
    }
    
    /* 左上の角のセル */
    thead th:first-child, .corner-header {
        background-color: #f2f2f2 !important; 
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        top: 0;
        left: 0;
        z-index: 100; /* 最前面に */
        min-width: 120px;
        max-width: 120px;
        text-align: center;
    }
    
    /* 状態セル */
    .status-cell {
        text-align: center;
        font-size: 18px;  /* 統一したフォントサイズ */
        min-width: 65px;
        vertical-align: middle;
        line-height: 1;
    }
    
    /* 状態アイコン */
    .status-icon {
        font-size: 18px;  /* 統一したフォントサイズ */
        font-weight: bold;
    }
    
    /* ステータスアイコン */
    .sold-out { color: #dc3545; }
    .last-one { color: #198754; }
    .locked { color: #6c757d; font-size: 18px; }  /* 統一したフォントサイズ */
    
    /* ラベル */
    .crowded-label { color: #fd7e14; font-weight: bold; }
    .crowded { color: #fd7e14; }
    
    /* 枠の完売数ラベル */
    .sold-out-count {
        display: block;
        font-size: 11px;
        font-weight: bold;
        background-color: #212529;
        color: white;
        padding: 2px 4px;
        border-radius: 4px;
        margin-top: 4px;
        text-align: center;
    }
    
    .sold-out-count.crowded {
        background-color: #fd7e14;
        color: black;
    }
    
    /* メンバー売上数ラベル */
    .member-sales-count {
        display: inline-block;
        font-size: 11px;
        font-weight: bold;
        background-color: #212529;
        color: white;
        padding: 2px 5px;
        border-radius: 4px;
        margin-left: 5px;
        float: right;
        min-width: 20px;
    }
    
    /* メンバー名のリンク */
    .member-link {
        color: #212529;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        max-width: 90px;
        word-wrap: break-word;
    }
    
    .member-link:hover {
        color: #0d6efd;
        text-decoration: underline;
    }
    
    /* ヘッダー */
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    .header h1 {
        color: #212529;
        font-weight: 700;
    }
    
    /* 更新時間 */
    .update-time {
        color: #6c757d;
        font-size: 14px;
        text-align: right;
        margin-bottom: 10px;
    }
    
    /* フィルターラベル */
    .filter-label {
        font-weight: 600;
        margin-bottom: 5px;
        font-size: 14px;
        color: #212529;
    }
    
    .legend-item {
        margin-right: 15px;
        display: inline-block;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
</style>
"""