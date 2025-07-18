# 🎙️ Chirp 模型對比與使用指南

## 📊 模型對比表

| 特性 | Chirp 1 | Chirp 2 |
|------|---------|---------|
| **流式識別 (StreamingRecognize)** | ❌ 不支持 | ✅ 支持 |
| **同步識別 (Recognize)** | ✅ 支持 | ✅ 支持 |
| **批量識別 (BatchRecognize)** | ✅ 支持 | ✅ 支持 |
| **自動語言檢測** | ✅ 支持 | ❌ 流式不支持 |
| **實時轉錄能力** | ❌ 無法實現 | ✅ 真正實時 |
| **準確率** | 高 | 更高 |
| **速度** | 快 | 更快 |

## 🎯 關鍵發現

### Chirp 1 的限制
- **不支持流式識別**：無法實現邊錄音邊轉錄
- 只能用於檔案轉錄或批量處理
- 雖然支持自動語言檢測，但無法實時處理

### Chirp 2 的優勢
- **支持流式識別**：真正的實時語音轉文字
- 更高的準確率和處理速度
- 支持中間結果顯示
- 但流式模式不支持自動語言檢測

## 🌍 Chirp 2 流式識別支持的語言

根據 Google Cloud 官方文檔，Chirp 2 的 `StreamingRecognize` 支持以下語言：

| 語言 | 語言代碼 |
|------|----------|
| 中文 (簡體，中國) | `cmn-Hans-CN` |
| 中文 (繁體，台灣) | `cmn-Hant-TW` |
| 中文 (粵語，香港) | `yue-Hant-HK` |
| 英文 (澳洲) | `en-AU` |
| 英文 (印度) | `en-IN` |
| 英文 (英國) | `en-GB` |
| 英文 (美國) | `en-US` |
| 法文 (加拿大) | `fr-CA` |
| 法文 (法國) | `fr-FR` |
| 德文 (德國) | `de-DE` |
| 義大利文 (義大利) | `it-IT` |
| 日文 (日本) | `ja-JP` |
| 韓文 (南韓) | `ko-KR` |
| 葡萄牙文 (巴西) | `pt-BR` |
| 西班牙文 (西班牙) | `es-ES` |
| 西班牙文 (美國) | `es-US` |

## 💡 使用建議

### 選擇 Chirp 2 的情況：
- ✅ 需要實時語音轉文字功能
- ✅ 對準確率要求較高
- ✅ 需要低延遲響應
- ✅ 已知要轉錄的語言

### 選擇 Chirp 1 的情況：
- ✅ 只需要檔案轉錄
- ✅ 需要自動語言檢測
- ✅ 批量處理音頻檔案
- ✅ 不需要實時處理

## 🚀 快速選擇指南

```bash
# 實時語音轉文字 (推薦)
./start.sh
# 選擇選項 1 - Chirp 2

# 基本檔案轉錄 
./start.sh  
# 選擇選項 3 - 檔案轉錄 (使用 Chirp 1)
```

## ⚠️ 重要提醒

1. **Chirp 2 流式模式不支持 `auto` 語言檢測**
2. **必須指定具體的語言代碼**
3. **不同地區可能支援的語言不同**
4. **流式識別有 25KB 限制每個請求**

## 📝 技術細節

### 錯誤修復過程
1. 原始問題：`realtime_chirp.py` 使用 Chirp 1 嘗試流式識別
2. 錯誤原因：Chirp 1 不支援 `StreamingRecognize`
3. 解決方案：創建 `realtime_chirp2.py` 使用 Chirp 2
4. 語言問題：Chirp 2 流式不支援 `auto` 和 `zh-TW`
5. 最終修復：使用正確的語言代碼 `cmn-Hant-TW`

這就是為什麼我們需要兩個不同的腳本來處理不同的使用場景！ 