def load_css():
    """
    アプリケーションのCSSスタイルを返す
    """
    return """
<style>
    /* テーブルコンテナの設定 - 重要: position: relative が必要 */
    .time-container {
        position: relative;
        overflow: auto;
        max-height: 80vh;
        max-width: 100%;
    }
    
    /* テーブル基本設定 */
    table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
    }
    
    /* セルの基本スタイル */
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        min-width: 65px;
        box-sizing: border-box;
        position: relative;
    }
    
    /* ヘッダーセル (時間枠) */
    thead th {
        background-color: #f2f2f2;
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    /* 最初の列 (メンバー名) */
    tbody td:first-child {
        background-color: #f2f2f2;
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        left: 0;
        z-index: 1;
        text-align: left;
        min-width: 120px;
    }
    
    /* 左上のセル (交差するところ) */
    thead th:first-child {
        background-color: #f2f2f2; 
        position: -webkit-sticky; /* Safari用 */
        position: sticky;
        top: 0;
        left: 0;
        z-index: 100; /* 最前面に */
    }
    
    /* 状態アイコン */
    .status-icon {
        font-size: 20px;
        font-weight: bold;
    }
    
    .sold-out {
        color: #dc3545;
    }
    
    .last-one {
        color: #198754;
    }
    
    .locked {
        color: #6c757d;
        font-size: 22px;
    }
    
    .crowded {
        color: #fd7e14;
    }
    
    /* 枠の完売数ラベル */
    .sold-out-count {
        display: block;
        font-size: 11px;
        font-weight: bold;
        background-color: #212529;
        color: white;
        padding: 2px 4px;
        border-radius: 4px;
        margin-top: 6px;
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
        cursor: pointer;
        display: inline-block;
        max-width: 90px;
        word-wrap: break-word;
    }
    
    .member-link:hover {
        color: #0d6efd;
        text-decoration: underline;
    }
    
    /* 混雑時間帯のラベル */
    .crowded-label {
        color: #fd7e14;
        font-weight: bold;
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
