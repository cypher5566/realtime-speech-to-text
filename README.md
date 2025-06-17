# 🎙️ Real-time Speech-to-Text with Google Cloud Chirp Models
# 實時語音轉文字 - Google Cloud Chirp 模型

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Speech--to--Text-orange.svg)](https://cloud.google.com/speech-to-text)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-lightgrey.svg)]()

A real-time speech-to-text transcription system using Google Cloud's latest **Chirp models** for high-accuracy, low-latency voice recognition with custom vocabulary support.

一個使用 Google Cloud 最新 **Chirp 模型** 的實時語音轉文字系統，支援高精度、低延遲的語音識別和自定義詞彙。

## ✨ Features | 主要功能

- 🎤 **Real-time Speech-to-Text** - Live transcription with instant results | 實時語音轉文字，即時顯示結果
- 🌍 **Multi-language Support** - Auto-detection for Chinese, English, Japanese, and more | 多語言自動檢測
- 🎯 **High Accuracy** - Powered by Google's advanced Chirp models | 使用 Google 先進的 Chirp 模型
- 📝 **Custom Vocabulary** - Professional terminology support with boost | 自定義詞彙支援，提升專業術語識別
- 🎨 **Beautiful Interface** - Color-coded output with real-time feedback | 彩色界面，實時反饋
- 📁 **File Transcription** - Support for various audio formats | 支援多種音頻格式轉錄

## 🚀 Quick Start | 快速開始

### Prerequisites | 環境準備

#### System Dependencies (macOS) | 系統依賴
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install portaudio (required for pyaudio)
brew install portaudio
```

#### Python Environment | Python 環境
```bash
# Clone the repository
git clone https://github.com/your-username/realtime-speech-to-text.git
cd realtime-speech-to-text

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Google Cloud Setup | Google Cloud 設置

```bash
# Install Google Cloud CLI (if not already installed)
brew install google-cloud-sdk

# Initialize gcloud
gcloud init

# Set up application default credentials
gcloud auth application-default login

# Enable Speech-to-Text API
gcloud services enable speech.googleapis.com

# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

### Run the Application | 運行應用

#### ⚡ One-Click Start (Recommended) | 一鍵啟動 (推薦)
```bash
./start.sh
```

#### 🔥 Manual Start | 手動啟動
```bash
# Activate environment
source venv/bin/activate

# Set project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Start real-time transcription (Chirp 2 - recommended)
python realtime_chirp2_fixed.py

# Or manage custom vocabulary
python custom_vocabulary.py
```

## 📋 Model Comparison | 模型對比

| Feature | Chirp 1 | Chirp 2 |
|---------|---------|---------|
| **Streaming Support** | ❌ No | ✅ Yes |
| **Real-time Latency** | High | Ultra-low |
| **Auto Language Detection** | ✅ Yes | ❌ No (streaming) |
| **Custom Vocabulary** | ✅ Yes | ✅ Yes |
| **Intermediate Results** | ❌ No | ✅ Yes |

**Recommendation:** Use **Chirp 2** (`realtime_chirp2_fixed.py`) for real-time applications.

## 🎛️ Custom Vocabulary | 自定義詞彙

The system includes a comprehensive vocabulary management tool for professional terminology:

```bash
python custom_vocabulary.py
```

**Pre-configured categories:**
- 💻 Technology: API, SDK, Docker, Kubernetes, Machine Learning
- 💼 Business: KPI, ROI, SaaS, B2B, MVP, Scalability  
- ☁️ Google Cloud: BigQuery, Cloud Storage, Cloud Run
- 🏢 Companies: VoiceTube, GitHub, Microsoft, Amazon

## 📂 Project Structure | 項目結構

```
realtime-speech-to-text/
├── 📄 README.md                    # Project documentation
├── 📋 requirements.txt             # Python dependencies
├── 🚀 start.sh                     # Interactive startup script
├── 🎤 realtime_chirp2_fixed.py     # Real-time transcription (Chirp 2)
├── 🎙️ realtime_chirp2.py           # Alternative Chirp 2 implementation
├── 📻 realtime_chirp.py            # Chirp 1 implementation
├── 📁 chirp_transcribe.py          # File transcription
├── 🎵 record_audio.py              # Audio recording utility
├── 📝 custom_vocabulary.py         # Vocabulary management
├── 📊 custom_vocabulary.json       # Vocabulary database
├── 📖 CHIRP_MODELS.md              # Model documentation
├── 🚫 .gitignore                   # Git ignore rules
└── 📁 venv/                        # Python virtual environment
```

## 🛠️ Technical Specifications | 技術規格

**Audio Configuration:**
- Sample Rate: 16kHz
- Channels: Mono
- Format: 16-bit PCM
- Chunk Size: ≤ 25,600 bytes

**API Configuration:**
- Model: `chirp_2` (recommended)
- Region: `us-central1`
- Encoding: LINEAR16
- Custom Vocabulary: Inline phrase sets with boost=10.0

## 🌍 Supported Languages | 支援語言

**Chirp 2 Streaming:**
- 🇺🇸 English (US/UK)
- 🇨🇳 Chinese (Simplified/Traditional)
- 🇯🇵 Japanese
- 🇰🇷 Korean
- 🇫🇷 French
- 🇩🇪 German
- 🇪🇸 Spanish
- 🇮🇹 Italian

## 🐛 Troubleshooting | 故障排除

### Common Issues | 常見問題

**1. Authentication Error**
```bash
gcloud auth application-default login
```

**2. API Not Enabled**
```bash
gcloud services enable speech.googleapis.com
```

**3. Microphone Permission (macOS)**
- System Preferences → Security & Privacy → Privacy → Microphone
- Allow Terminal to access microphone

**4. PyAudio Installation Error**
```bash
brew install portaudio
pip install pyaudio
```

**5. Audio Chunk Size Error**
- The system automatically handles chunk size limits (25KB max)
- Use `realtime_chirp2_fixed.py` for proper chunk management

## 🔧 Configuration | 配置

Customize audio settings in the Python files:

```python
# Audio quality settings
RATE = 16000  # Sample rate (8000, 16000, 44100)
CHUNK = int(RATE / 10)  # Buffer size

# Speech detection sensitivity
speech_start_timeout=15  # Wait time for speech start
speech_end_timeout=15    # Wait time after speech end
```

## 🤝 Contributing | 貢獻

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License | 授權

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments | 致謝

- Google Cloud Speech-to-Text team for the Chirp models
- Python audio processing community
- All contributors and testers

## 🎉 Get Started | 開始體驗

Ready to experience the power of Chirp's speech recognition?

```bash
# Activate environment
source venv/bin/activate

# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Start real-time transcription
python realtime_chirp2_fixed.py
```

**Prepare to be amazed by Chirp's accuracy!** | **準備好被 Chirp 的精準度震撼了嗎？**
