"""
Data Checker for CSV and Excel Files

このモジュールは、CSVおよびExcelファイルのデータチェックを行います。
- Nullチェック
- 重複チェック  
- 異常値チェック
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict
import json


def detect_file_type(filepath: str) -> str:
    """
    ファイルの拡張子からファイルタイプを判別する
    
    Args:
        filepath: ファイルパス
        
    Returns:
        'csv' または 'excel'
        
    Raises:
        ValueError: サポートされていないファイルタイプの場合
    """
    ext = Path(filepath).suffix.lower()
    
    if ext == '.csv':
        return 'csv'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    else:
        raise ValueError(f"サポートされていないファイルタイプ: {ext}")


def load_csv_data(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    CSVファイルを読み込む
    
    Args:
        filepath: CSVファイルのパス
        
    Returns:
        シート名をキーとしたDataFrameの辞書（CSVの場合はファイル名がキー）
    """
    filename = Path(filepath).stem
    df = pd.read_csv(filepath)
    return {filename: df}


def load_excel_data(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    Excelファイルの全シートを読み込む
    
    Args:
        filepath: Excelファイルのパス
        
    Returns:
        シート名をキーとしたDataFrameの辞書
    """
    excel_file = pd.ExcelFile(filepath)
    data_dict = {}
    
    for sheet_name in excel_file.sheet_names:
        data_dict[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    return data_dict


def load_data(filepath: str) -> Dict[str, pd.DataFrame]:
    """
    ファイルタイプを自動判別してデータを読み込む
    
    Args:
        filepath: ファイルパス
        
    Returns:
        シート名をキーとしたDataFrameの辞書
    """
    file_type = detect_file_type(filepath)
    
    if file_type == 'csv':
        return load_csv_data(filepath)
    else:  # excel
        return load_excel_data(filepath)


def check_null(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    列ごとにNullチェックを行う
    
    Args:
        df: チェック対象のDataFrame
        
    Returns:
        列名をキーとした辞書。各列のNull数、Null率、Nullの行インデックスを含む
    """
    result = {}
    
    for column in df.columns:
        null_mask = df[column].isna()
        null_count = null_mask.sum()
        total_count = len(df)
        null_ratio = null_count / total_count if total_count > 0 else 0
        null_indices = df[null_mask].index.tolist()
        
        result[column] = {
            'null_count': int(null_count),
            'total_count': int(total_count),
            'null_ratio': float(null_ratio),
            'null_indices': null_indices[:100]  # 最初の100件まで記録
        }
    
    return result


def check_duplicates(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    列ごとに重複チェックを行う
    
    Args:
        df: チェック対象のDataFrame
        
    Returns:
        列名をキーとした辞書。各列の重複数、重複率、重複値を含む
    """
    result = {}
    
    for column in df.columns:
        # Null値を除外して重複をチェック
        non_null_series = df[column].dropna()
        total_count = len(non_null_series)
        unique_count = non_null_series.nunique()
        duplicate_count = total_count - unique_count
        duplicate_ratio = duplicate_count / total_count if total_count > 0 else 0
        
        # 重複している値を取得
        duplicated_values = non_null_series[non_null_series.duplicated(keep=False)].unique()
        
        result[column] = {
            'total_count': int(total_count),
            'unique_count': int(unique_count),
            'duplicate_count': int(duplicate_count),
            'duplicate_ratio': float(duplicate_ratio),
            'duplicated_values': duplicated_values[:100].tolist()  # 最初の100件まで記録
        }
    
    return result


def check_outliers(df: pd.DataFrame, threshold: float = 3.0) -> Dict[str, Dict]:
    """
    列ごとに異常値チェックを行う（数値列のみ）
    
    Zスコア法を使用して、指定された閾値を超える値を異常値とする
    
    Args:
        df: チェック対象のDataFrame
        threshold: Zスコアの閾値（デフォルト: 3.0）
        
    Returns:
        列名をキーとした辞書。各列の異常値数、異常値率、異常値の行インデックスを含む
    """
    result = {}
    
    for column in df.columns:
        # 数値型の列のみチェック
        if pd.api.types.is_numeric_dtype(df[column]):
            # Null値を除外
            non_null_series = df[column].dropna()
            
            if len(non_null_series) > 0:
                # Zスコアを計算
                mean = non_null_series.mean()
                std = non_null_series.std()
                
                if std > 0:
                    # Null値を除外したデータに対してZスコアを計算
                    z_scores = np.abs((non_null_series - mean) / std)
                    outlier_mask = z_scores > threshold
                    outlier_count = outlier_mask.sum()
                    
                    # 元のDataFrameでの行インデックスを取得
                    outlier_indices = non_null_series[outlier_mask].index.tolist()
                    outlier_ratio = outlier_count / len(df) if len(df) > 0 else 0
                    
                    result[column] = {
                        'outlier_count': int(outlier_count),
                        'total_count': len(df),
                        'outlier_ratio': float(outlier_ratio),
                        'outlier_indices': outlier_indices[:100],  # 最初の100件まで記録
                        'mean': float(mean),
                        'std': float(std),
                        'threshold': float(threshold)
                    }
                else:
                    # 標準偏差が0の場合（すべての値が同じ）
                    result[column] = {
                        'outlier_count': 0,
                        'total_count': len(df),
                        'outlier_ratio': 0.0,
                        'outlier_indices': [],
                        'mean': float(mean),
                        'std': 0.0,
                        'threshold': float(threshold),
                        'note': '標準偏差が0のため異常値なし'
                    }
            else:
                result[column] = {
                    'outlier_count': 0,
                    'total_count': 0,
                    'outlier_ratio': 0.0,
                    'outlier_indices': [],
                    'note': 'データなし'
                }
        else:
            # 数値型でない列はスキップ
            result[column] = {
                'note': '数値型ではないためスキップ'
            }
    
    return result


def perform_checks(df: pd.DataFrame, outlier_threshold: float = 3.0) -> Dict:
    """
    データフレームに対して全てのチェックを実行
    
    Args:
        df: チェック対象のDataFrame
        outlier_threshold: 異常値判定のZスコア閾値
        
    Returns:
        全チェック結果を含む辞書
    """
    return {
        'null_check': check_null(df),
        'duplicate_check': check_duplicates(df),
        'outlier_check': check_outliers(df, outlier_threshold)
    }


def check_file(filepath: str, output_filepath: str = None, outlier_threshold: float = 3.0) -> Dict:
    """
    ファイルのデータチェックを実行し、結果を出力
    
    Args:
        filepath: チェック対象のファイルパス
        output_filepath: 結果出力先のファイルパス（省略時は自動生成）
        outlier_threshold: 異常値判定のZスコア閾値
        
    Returns:
        全チェック結果を含む辞書
    """
    # データを読み込み
    data_dict = load_data(filepath)
    
    # 各シート/ファイルに対してチェックを実行
    results = {}
    for sheet_name, df in data_dict.items():
        results[sheet_name] = perform_checks(df, outlier_threshold)
    
    # 出力ファイルパスを決定
    if output_filepath is None:
        input_path = Path(filepath)
        output_filepath = input_path.parent / f"{input_path.stem}_check_result.json"
    
    # 結果をJSON形式で出力
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"チェック結果を {output_filepath} に出力しました。")
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python data_checker.py <ファイルパス> [出力ファイルパス] [異常値閾値]")
        print("例: python data_checker.py data.csv")
        print("例: python data_checker.py data.xlsx output.json 3.0")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_filepath = sys.argv[2] if len(sys.argv) > 2 else None
    outlier_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    
    try:
        check_file(filepath, output_filepath, outlier_threshold)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
