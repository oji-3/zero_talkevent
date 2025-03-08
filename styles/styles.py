def load_css():
    """
    アプリケーションのCSSスタイルを返す
    """
    return """
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
    .locked {
        color: #6c757d;
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
        writing-mode: horizontal-tb; /* 水平方向に表示 */
        transform: none; /* 回転を削除 */
        height: auto; /* 高さを自動調整 */
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        padding: 8px 4px;
    }
    /* 枠の完売数ラベルのスタイル */
    .sold-out-count {
        display: block;
        font-size: 11px;
        font-weight: bold;
        background-color: #212529;
        color: white;
        padding: 2px 4px;
        border-radius: 4px;
        margin-top: 6px; /* 下に表示するのでtopマージンに変更 */
        text-align: center;
    }
    
    /* 混雑時間帯の完売数ラベルのスタイル */
    .sold-out-count.crowded {
        background-color: #fd7e14;
        color: black;
    }
    
    /* 数字の回転を削除 */
    .sold-out-count-number {
        display: inline-block;
        transform: none; /* 回転を削除 */
    }
    /* オレンジ文字(混雑時間帯)を通常表示に変更 */
    .crowded-label {
        writing-mode: horizontal-tb;
        transform: none;
        display: inline;
        color: #fd7e14;
        font-weight: bold;
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
        text-align: center;
        float: right;
        min-width: 20px;
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
        /* 上部固定のみ適用 */
        position: sticky;
        top: 0;
        z-index: 1;
    }
    /* メンバー名の列の固定を完全に解除 */
    th:first-child {
        position: static; /* stickyからstaticに変更 */
        background-color: #f2f2f2;
        min-width: 100px; 
        max-width: 120px;
        left: auto; /* 明示的に左固定を解除 */
        z-index: auto; /* z-indexも自動に */
    }
    td:first-child {
        position: static; /* stickyからstaticに変更 */
        left: auto; /* 明示的に左固定を解除 */
        background-color: #f2f2f2;
        font-weight: bold;
        z-index: auto; /* z-indexも自動に */
        max-width: 100px;      /* セルの最大幅を制限 */
        word-wrap: break-word; /* 長い単語も折り返し */
        white-space: normal;   /* テキストを折り返し */
        text-align: left;      /* 左寄せ */
        line-height: 1.3;      /* 行間を少し狭く */
        min-width: 100px;
    }
    /* 時間のヘッダー部分は上部固定のみ */
    th:not(:first-child) {
        position: sticky;
        top: 0;
        left: auto;
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
        word-break: keep-all;  /* 単語の途中での改行を防ぐ */
        display: inline-block; /* インラインブロック要素として表示 */
        max-width: 90px;       /* リンク要素の最大幅 */
        word-wrap: break-word; /* 長い単語も折り返し */
    }
    .member-link:hover {
        color: #0d6efd;
        text-decoration: underline;
    }
    .legend-item {
        margin-right: 15px;
        display: inline-block;
    }
</style>
"""