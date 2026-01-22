"""
データチェッカーの使用例

このスクリプトは、data_checker.pyの使い方を示します。
"""

import pandas as pd
from data_checker import (
    load_data,
    check_null,
    check_duplicates,
    check_outliers,
    perform_checks,
    check_file
)


def example_basic_usage():
    """基本的な使い方の例"""
    print("=" * 60)
    print("例1: ファイル全体のチェック")
    print("=" * 60)
    
    # ファイル全体をチェックして結果を出力
    results = check_file("sample_data.csv")
    
    print("\n完了しました。結果ファイルを確認してください。\n")


def example_individual_checks():
    """個別のチェック関数を使う例"""
    print("=" * 60)
    print("例2: 個別のチェック関数を使用")
    print("=" * 60)
    
    # データを読み込み
    data_dict = load_data("sample_data.csv")
    
    # 最初のシート/ファイルを取得
    sheet_name = list(data_dict.keys())[0]
    df = data_dict[sheet_name]
    
    print(f"\nシート名: {sheet_name}")
    print(f"データサイズ: {df.shape}")
    print("\n--- データのプレビュー ---")
    print(df.head())
    
    # Nullチェック
    print("\n--- Nullチェック ---")
    null_results = check_null(df)
    for col, result in null_results.items():
        if result['null_count'] > 0:
            print(f"{col}: {result['null_count']}個のNull ({result['null_ratio']:.2%})")
    
    # 重複チェック
    print("\n--- 重複チェック ---")
    dup_results = check_duplicates(df)
    for col, result in dup_results.items():
        if result['duplicate_count'] > 0:
            print(f"{col}: {result['duplicate_count']}個の重複 ({result['duplicate_ratio']:.2%})")
    
    # 異常値チェック
    print("\n--- 異常値チェック ---")
    outlier_results = check_outliers(df, threshold=2.0)
    for col, result in outlier_results.items():
        if 'outlier_count' in result and result['outlier_count'] > 0:
            print(f"{col}: {result['outlier_count']}個の異常値 ({result['outlier_ratio']:.2%})")
    
    print("\n")


def example_create_excel():
    """Excelファイルを作成してテストする例"""
    print("=" * 60)
    print("例3: Excelファイルのチェック")
    print("=" * 60)
    
    # サンプルExcelファイルを作成
    df1 = pd.DataFrame({
        'ID': [1, 2, 3, 4, 5],
        '名前': ['田中', '佐藤', '鈴木', '田中', None],
        '年齢': [25, 30, 28, 25, 35],
        'スコア': [85, 92, 78, 85, 150]  # 150は異常値
    })
    
    df2 = pd.DataFrame({
        'コード': ['A001', 'A002', 'A003', None, 'A005'],
        '売上': [100000, 200000, 150000, 180000, 5000000],  # 5000000は異常値
        '地域': ['東京', '大阪', '東京', '名古屋', '東京']
    })
    
    with pd.ExcelWriter('sample_data.xlsx', engine='openpyxl') as writer:
        df1.to_excel(writer, sheet_name='社員データ', index=False)
        df2.to_excel(writer, sheet_name='売上データ', index=False)
    
    print("sample_data.xlsx を作成しました。")
    
    # Excelファイルをチェック
    results = check_file("sample_data.xlsx", "sample_data_excel_result.json")
    
    print("\n完了しました。結果ファイルを確認してください。\n")


if __name__ == "__main__":
    print("\nデータチェッカーの使用例\n")
    
    try:
        # 例1: 基本的な使い方
        example_basic_usage()
        
        # 例2: 個別のチェック関数
        example_individual_checks()
        
        # 例3: Excelファイルのチェック
        example_create_excel()
        
        print("=" * 60)
        print("すべての例が正常に実行されました！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
