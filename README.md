# data-check

CSVおよびExcelファイルのデータチェックツール

## 概要

このツールは、CSVファイルやExcelファイルのデータ品質をチェックするためのPythonライブラリです。以下のチェックを列ごとに実行し、結果をJSON形式で出力します。

- **Nullチェック**: 欠損値（null値）の検出
- **重複チェック**: 重複する値の検出
- **異常値チェック**: 統計的に異常な値の検出（数値列のみ、Zスコア法を使用）

## 機能

- CSVとExcelファイルの自動判別
- Excelファイルは全シートを読み込み
- 列ごとに詳細なチェックを実行
- 結果をJSON形式で出力
- コマンドラインとPythonライブラリの両方として使用可能

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### コマンドラインから使用

```bash
# 基本的な使い方
python data_checker.py sample_data.csv

# 出力ファイルを指定
python data_checker.py sample_data.csv output.json

# 異常値判定の閾値を指定（デフォルト: 3.0）
python data_checker.py sample_data.xlsx output.json 2.5
```

### Pythonスクリプトから使用

```python
from data_checker import check_file, load_data, check_null, check_duplicates, check_outliers

# ファイル全体をチェック
results = check_file("data.csv")

# データを読み込んで個別にチェック
data_dict = load_data("data.xlsx")
for sheet_name, df in data_dict.items():
    null_results = check_null(df)
    dup_results = check_duplicates(df)
    outlier_results = check_outliers(df, threshold=3.0)
```

## 使用例

サンプルデータとサンプルスクリプトが含まれています。

```bash
# サンプルスクリプトを実行
python example_usage.py
```

このスクリプトは以下を実行します：
1. CSVファイルのチェック
2. 個別のチェック関数の使用例
3. Excelファイルの作成とチェック

## 出力形式

チェック結果はJSON形式で出力されます。各シート/ファイルごとに以下の情報が含まれます：

```json
{
  "シート名": {
    "null_check": {
      "列名": {
        "null_count": 2,
        "total_count": 100,
        "null_ratio": 0.02,
        "null_indices": [10, 25]
      }
    },
    "duplicate_check": {
      "列名": {
        "total_count": 98,
        "unique_count": 80,
        "duplicate_count": 18,
        "duplicate_ratio": 0.18,
        "duplicated_values": ["値1", "値2"]
      }
    },
    "outlier_check": {
      "列名": {
        "outlier_count": 3,
        "total_count": 100,
        "outlier_ratio": 0.03,
        "outlier_indices": [5, 42, 89],
        "mean": 50.5,
        "std": 15.2,
        "threshold": 3.0
      }
    }
  }
}
```

## チェック詳細

### Nullチェック
- 各列の欠損値（NaN、None、空値など）を検出
- Null数、Null率、Nullの行インデックスを記録

### 重複チェック
- 各列の重複する値を検出（Null値は除外）
- 重複数、重複率、重複している値を記録

### 異常値チェック
- 数値列のみ対象
- Zスコア法を使用して異常値を検出
- デフォルトの閾値は3.0（標準偏差の3倍以上）
- 異常値の数、率、行インデックス、統計情報を記録

## ファイル構成

- `data_checker.py`: メインモジュール
- `example_usage.py`: 使用例
- `sample_data.csv`: サンプルCSVファイル
- `requirements.txt`: 依存パッケージ

## 必要なライブラリ

- pandas >= 2.0.0
- numpy >= 1.24.0
- openpyxl >= 3.0.0 (Excelファイルの読み込みに必要)

## ライセンス

MIT License