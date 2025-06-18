#!/bin/bash

# 🎙️ Chirp 實時語音轉文字啟動腳本

echo "🎙️ 啟動 Chirp 實時語音轉文字..."
echo "============================================"

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境不存在，正在創建..."
    python3 -m venv venv
    echo "✅ 虛擬環境創建完成"
fi

# 激活虛擬環境
echo "🔄 激活虛擬環境..."
source venv/bin/activate

# 檢查依賴是否安裝
if ! python -c "import google.cloud.speech_v2, pyaudio" 2>/dev/null; then
    echo "📦 安裝依賴包..."
    pip install -r requirements.txt
    echo "✅ 依賴安裝完成"
fi

# 設置環境變量
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "⚠️  請設置您的 Google Cloud 項目 ID:"
    read -p "輸入項目 ID: " project_id
    export GOOGLE_CLOUD_PROJECT="$project_id"
    echo "✅ 項目 ID 已設置: $project_id"
else
    echo "✅ 使用項目: $GOOGLE_CLOUD_PROJECT"
fi

echo ""
echo "🚀 選擇功能:"
echo "1. 🎤 實時語音轉文字 - Chirp 2 修復版 (推薦，已修復編碼問題)"
echo "2. ⏱️ 連續實時轉錄 - 無時間限制 (自動處理5分鐘限制)"
echo "3. 🎤 實時語音轉文字 - Chirp 2 原版 (可能有編碼問題)"
echo "4. 🎤 實時語音轉文字 - Chirp 1 (基本，不支持流式)"
echo "5. 📁 轉錄音頻檔案"
echo "6. 🎙️ 錄製測試音頻"
echo "7. 📚 管理自定義詞彙 (專業術語)"
echo ""

read -p "請選擇 (1-7): " choice

case $choice in
    1)
        echo "🎤 啟動實時語音轉文字 - Chirp 2 修復版..."
        echo "✨ 已修復編碼問題，應該可以正常轉錄語音"
        python realtime_chirp2_fixed.py
        ;;
    2)
        echo "⏱️ 啟動連續實時轉錄 - 無時間限制..."
        echo "🚀 自動處理 Google Cloud 5分鐘流式限制"
        echo "✨ 支持無限時長錄音，自動重新連接"
        python realtime_chirp2_continuous.py
        ;;
    3)
        echo "🎤 啟動實時語音轉文字 - Chirp 2 原版..."
        echo "⚠️  注意: 可能有編碼問題"
        python realtime_chirp2.py
        ;;
    4)
        echo "🎤 啟動實時語音轉文字 - Chirp 1..."
        echo "⚠️  注意: Chirp 1 不支持流式識別，將使用分段處理"
        python realtime_chirp.py
        ;;
    5)
        echo "📁 啟動音頻檔案轉錄..."
        python chirp_transcribe.py
        ;;
    6)
        echo "🎙️ 啟動音頻錄製..."
        python record_audio.py
        ;;
    7)
        echo "📚 啟動自定義詞彙管理..."
        python custom_vocabulary.py
        ;;
    *)
        echo "❌ 無效選擇，啟動連續實時轉錄..."
        python realtime_chirp2_continuous.py
        ;;
esac 