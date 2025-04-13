# LLMPack

LLMPack は、コードファイルを1つのマークダウンドキュメントにまとめるコマンドラインツールで、LLM（大規模言語モデル）での使用を目的としています。

[English README](README.md)

## 特徴

- ディレクトリツリー構造の生成
- コードファイルを1つのマークダウンドキュメントにまとめる
- `.gitignore` パターンの尊重
- 出力を自動的にクリップボードにコピー（macOSのみ）
- 進捗表示付きのリッチなターミナル出力

## インストール

### Homebrew を使用（macOS/Linux）

```bash
# Homebrew tap からインストール
brew tap harukaxq/tools
brew install llmpack
```

### ソースからインストール

```bash
# リポジトリをクローン
git clone https://github.com/harukaxq/llmpack.git
cd llmpack

# 開発モードでインストール
pip install -e .
```

## 使用方法

プロジェクトディレクトリで `llmpack` コマンドを実行します：

```bash
# 基本的な使用法
llmpack

# カスタム出力ファイルを指定
llmpack -o output.md

# 各ファイルの先頭にプレフィックスを追加
llmpack -p "ここにプレフィックステキストを入力"

# 詳細出力を有効化
llmpack -v

# クリップボードへのコピーを無効化
llmpack --no-clipboard
```

## オプション

- `-p, --prefix`: 各ファイルの先頭に追加するテキスト
- `-o, --output`: 出力ファイルのパス（デフォルト: `.llmpack_files.md`）
- `-v, --verbose`: 詳細出力を有効化
- `--no-clipboard`: クリップボードへのコピーを無効化

## 出力フォーマット

生成されるマークダウンファイルには以下が含まれます：

1. ディレクトリ構造
2. `README.md`、`package.json`、`pyproject.toml`の内容（存在する場合）
3. すべてのコードファイルの内容（サポートされている拡張子）

各ファイルは以下のようにフォーマットされます：

```markdown
# path/to/file.ext
<content>
ファイルの内容がここに表示されます...
</content>
```

## サポートされているファイル拡張子

LLMPackは以下を含む幅広いファイル拡張子をサポートしています：

- Web: `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.less`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`, `.cjs`
- Webフレームワーク: `.svelte`, `.vue`, `.prisma`
- Python: `.py`
- 設定ファイル: `.json`, `.yml`, `.yaml`, `.toml`
- その他多数...

## ライセンス

MIT
