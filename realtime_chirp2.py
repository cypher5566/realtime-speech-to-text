#!/usr/bin/env python3
"""
實時語音轉文字 - 使用 Google Cloud Speech-to-Text Chirp 2 模型
邊錄音邊轉錄！（Chirp 2 支持流式識別）
"""

import os
import threading
import time
import queue
import pyaudio
from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

# 音頻配置
RATE = 16000  # 採樣率
CHUNK = int(RATE / 10)  # 100ms 的音頻數據


class RealTimeTranscriberChirp2:
    def __init__(self, region="us-central1", language_code="en-US"):
        self.client = SpeechClient(
            client_options=ClientOptions(
                api_endpoint=f"{region}-speech.googleapis.com",
            )
        )
        self.region = region
        self.language_code = language_code
        self.audio_queue = queue.Queue()
        self.recording = False
        
    def get_config(self):
        """獲取 Chirp 2 語音識別配置"""
        return cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[self.language_code],
            model="chirp_2",  # 使用 Chirp 2 模型
        )
    
    def audio_generator(self):
        """音頻數據生成器，用於流式 API"""
        chunk_count = 0
        while self.recording:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    print(f"\n🔚 音頻生成器停止，共處理 {chunk_count} 個音頻塊")
                    return
                chunk_count += 1
                
                # 每處理100個音頻塊顯示一次狀態
                if chunk_count % 100 == 0:
                    print(f"\r🎵 已發送 {chunk_count} 個音頻塊...", end='', flush=True)
                
                yield chunk
            except queue.Empty:
                continue
            except Exception as e:
                print(f"音頻生成器錯誤: {e}")
                return
    
    def record_audio(self):
        """錄製音頻線程"""
        p = pyaudio.PyAudio()
        
        # 檢查麥克風設備
        try:
            # 列出可用的音頻設備
            device_count = p.get_device_count()
            print(f"🎤 檢測到 {device_count} 個音頻設備")
            
            # 尋找默認輸入設備
            default_input = p.get_default_input_device_info()
            print(f"🎙️  使用麥克風: {default_input['name']}")
            
        except Exception as e:
            print(f"⚠️  音頻設備檢測錯誤: {e}")
        
        stream = None
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=None,  # 使用默認麥克風
            )
            
            print("✅ 麥克風已連接，開始錄音...")
            print("🔊 請說話...")
            
            while self.recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    if self.recording:  # 再次檢查，避免停止時還在添加數據
                        self.audio_queue.put(data)
                except Exception as e:
                    print(f"讀取音頻錯誤: {e}")
                    break
                
        except Exception as e:
            print(f"❌ 麥克風錯誤: {e}")
            print("💡 請檢查:")
            print("   1. 麥克風是否連接正常")
            print("   2. 系統偏好設定 → 安全性與隱私權 → 隱私權 → 麥克風")
            print("   3. 允許終端機存取麥克風")
            self.recording = False
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()
    
    def create_streaming_requests(self):
        """創建流式請求生成器 - Chirp 2 版本"""
        # 第一個請求包含配置
        config = self.get_config()
        recognizer = f"projects/{PROJECT_ID}/locations/{self.region}/recognizers/_"
        
        # Chirp 2 的流式配置，增加中間結果和語音活動檢測
        streaming_config = cloud_speech.StreamingRecognitionConfig(
            config=config,
            streaming_features=cloud_speech.StreamingRecognitionFeatures(
                interim_results=True,  # 啟用中間結果
                voice_activity_timeout=cloud_speech.StreamingRecognitionFeatures.VoiceActivityTimeout(
                    speech_start_timeout=30,  # 等待開始說話的時間
                    speech_end_timeout=30,    # 檢測到說話結束後的等待時間
                ),
            ),
        )
        
        initial_request = cloud_speech.StreamingRecognizeRequest(
            recognizer=recognizer,
            streaming_config=streaming_config,
        )
        
        yield initial_request
        
        # 後續請求只包含音頻數據
        for audio_chunk in self.audio_generator():
            yield cloud_speech.StreamingRecognizeRequest(audio=audio_chunk)
    
    def start_streaming(self):
        """開始流式轉錄"""
        print("🚀 啟動實時語音轉文字 - Chirp 2...")
        print("=" * 60)
        print("✨ Chirp 2 新特色:")
        print("   - 支持流式識別（實時轉錄）")
        print("   - 更高的準確率和速度")
        print("   - 支持多語言自動檢測")
        print("   - 按 Ctrl+C 停止")
        print("=" * 60)
        
        self.recording = True
        
        # 開始錄音線程
        audio_thread = threading.Thread(target=self.record_audio)
        audio_thread.daemon = True
        audio_thread.start()
        
        # 等待錄音線程啟動並累積一些音頻數據
        print("⏳ 等待音頻數據累積...")
        time.sleep(3)  # 增加等待時間
        
        if not self.recording:
            print("❌ 麥克風初始化失敗，無法繼續")
            return
            
        # 檢查是否有音頻數據
        if self.audio_queue.empty():
            print("⚠️  警告: 沒有檢測到音頻數據，請檢查麥克風")
            print("🎤 請嘗試說話，然後按 Enter 繼續...")
            input()
        
        try:
            print("🌐 連接 Google Cloud Speech API (Chirp 2)...")
            
            # 創建流式請求
            requests = self.create_streaming_requests()
            
            # 開始流式識別
            responses = self.client.streaming_recognize(requests=requests)
            
            print("🎯 API 連接成功，開始實時轉錄...")
            
            # 處理響應
            self.process_responses(responses)
            
        except KeyboardInterrupt:
            print("\n\n🛑 停止錄音...")
        except Exception as e:
            print(f"\n❌ 轉錄錯誤: {e}")
            print("💡 可能的解決方案:")
            print("   1. 檢查網路連接")
            print("   2. 確認 Google Cloud 認證正確")
            print("   3. 檢查 Speech-to-Text API 是否已啟用")
            print("   4. 確認麥克風權限")
            print("   5. 確保有足夠的音頻數據")
            import traceback
            traceback.print_exc()
        finally:
            self.recording = False
            self.audio_queue.put(None)  # 停止音頻生成器
    
    def process_responses(self, responses):
        """處理流式響應"""
        print("\n🎯 開始實時轉錄:")
        print("-" * 60)
        print("💡 提示: 請清晰說話，您會看到:")
        print("   🔘 灰色文字 = 正在識別中")  
        print("   ✅ 綠色文字 = 確認結果")
        print("-" * 60)
        
        num_chars_printed = 0
        response_count = 0
        
        try:
            for response in responses:
                response_count += 1
                
                # 調試信息：每收到10個響應顯示一次心跳
                if response_count % 10 == 0:
                    print(f"\r💓 已處理 {response_count} 個響應...", end='', flush=True)
                
                if not response.results:
                    print(f"\r🔄 等待語音輸入...", end='', flush=True)
                    continue
                
                result = response.results[0]
                if not result.alternatives:
                    continue
                
                transcript = result.alternatives[0].transcript.strip()
                if not transcript:
                    continue
                
                # 清除之前的狀態訊息
                print(f"\r{' ' * 50}", end='', flush=True)
                
                # 清除之前的中間結果
                overwrite_chars = ' ' * max(0, num_chars_printed - len(transcript))
                
                if not result.is_final:
                    # 中間結果 - 灰色顯示
                    print(f"\r🔘 \033[90m{transcript}{overwrite_chars}\033[0m", end='', flush=True)
                    num_chars_printed = len(transcript) + 3  # 包含 "🔘 "
                else:
                    # 最終結果 - 綠色顯示
                    print(f"\r✅ \033[92m{transcript}\033[0m{overwrite_chars}")
                    
                    # 如果有檢測到的語言，顯示
                    if hasattr(result, 'language_code') and result.language_code:
                        print(f"   \033[94m[語言: {result.language_code}]\033[0m")
                    
                    num_chars_printed = 0
                    print("-" * 60)
                    
        except Exception as e:
            print(f"\n處理響應時出錯: {e}")
            import traceback
            traceback.print_exc()


def main():
    if not PROJECT_ID:
        print("❌ 錯誤: 請設置 GOOGLE_CLOUD_PROJECT 環境變量")
        print("執行: export GOOGLE_CLOUD_PROJECT=your-project-id")
        return
    
    print("🎙️  實時語音轉文字 - Chirp 2 模型")
    print("=" * 60)
    print(f"📍 項目: {PROJECT_ID}")
    print("🆕 使用 Chirp 2 - 支持流式識別！")
    
    # 選擇語言模式
    print("\n🌍 語言設置 (Chirp 2 流式識別支持的語言):")
    print("1. 英文 (美國) - 推薦")
    print("2. 中文簡體")
    print("3. 中文繁體 (台灣)")
    print("4. 英文 (英國)")
    print("5. 日文")
    print("6. 韓文")
    print("7. 法文")
    print("8. 德文")
    print("9. 西班牙文")
    print("10. 義大利文")
    
    choice = input("\n請選擇 (1-10, 默認: 1): ").strip() or "1"
    
    # 根據文檔，Chirp 2 流式識別支持的語言
    language_map = {
        "1": "en-US",        # 英文美國
        "2": "cmn-Hans-CN",  # 中文簡體
        "3": "cmn-Hant-TW",  # 中文繁體
        "4": "en-GB",        # 英文英國
        "5": "ja-JP",        # 日文
        "6": "ko-KR",        # 韓文
        "7": "fr-FR",        # 法文
        "8": "de-DE",        # 德文
        "9": "es-US",        # 西班牙文
        "10": "it-IT"        # 義大利文
    }
    
    language = language_map.get(choice, "auto")
    print(f"🗣️  語言設置: {language}")
    
    # 創建轉錄器
    transcriber = RealTimeTranscriberChirp2(language_code=language)
    
    # 開始轉錄
    transcriber.start_streaming()


if __name__ == "__main__":
    main() 