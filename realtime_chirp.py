#!/usr/bin/env python3
"""
實時語音轉文字 - 使用 Google Cloud Speech-to-Text Chirp 模型
邊錄音邊轉錄！
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


class RealTimeTranscriber:
    def __init__(self, region="us-central1", language_code="auto"):
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
        """獲取 Chirp 語音識別配置"""
        return cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[self.language_code],
            model="chirp",
        )
    
    def audio_generator(self):
        """音頻數據生成器，用於流式 API"""
        while self.recording:
            try:
                chunk = self.audio_queue.get(timeout=1)
                if chunk is None:
                    return
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
        """創建流式請求生成器"""
        # 第一個請求包含配置
        config = self.get_config()
        recognizer = f"projects/{PROJECT_ID}/locations/{self.region}/recognizers/_"
        
        initial_request = cloud_speech.StreamingRecognizeRequest(
            recognizer=recognizer,
            streaming_config=cloud_speech.StreamingRecognitionConfig(
                config=config,
                streaming_features=cloud_speech.StreamingRecognitionFeatures(
                    interim_results=True,  # 顯示中間結果
                    voice_activity_timeout=cloud_speech.StreamingRecognitionFeatures.VoiceActivityTimeout(
                        speech_start_timeout=15,  # 等待開始說話的時間
                        speech_end_timeout=15,    # 檢測到說話結束後的等待時間
                    ),
                ),
            ),
        )
        
        yield initial_request
        
        # 後續請求只包含音頻數據
        for audio_chunk in self.audio_generator():
            yield cloud_speech.StreamingRecognizeRequest(audio=audio_chunk)
    
    def start_streaming(self):
        """開始流式轉錄"""
        print("🚀 啟動實時語音轉文字...")
        print("=" * 60)
        print("💡 說話技巧:")
        print("   - 說話清晰，避免背景噪音")
        print("   - 短暫停頓會觸發最終結果")
        print("   - 支持多種語言自動檢測")
        print("   - 按 Ctrl+C 停止")
        print("=" * 60)
        
        self.recording = True
        
        # 開始錄音線程
        audio_thread = threading.Thread(target=self.record_audio)
        audio_thread.daemon = True
        audio_thread.start()
        
        # 等待錄音線程啟動
        import time
        time.sleep(1)
        
        if not self.recording:
            print("❌ 麥克風初始化失敗，無法繼續")
            return
        
        try:
            print("🌐 連接 Google Cloud Speech API...")
            
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
            import traceback
            traceback.print_exc()
        finally:
            self.recording = False
            self.audio_queue.put(None)  # 停止音頻生成器
    
    def process_responses(self, responses):
        """處理流式響應"""
        print("\n🎯 開始實時轉錄:")
        print("-" * 60)
        
        num_chars_printed = 0
        
        try:
            for response in responses:
                if not response.results:
                    continue
                
                result = response.results[0]
                if not result.alternatives:
                    continue
                
                transcript = result.alternatives[0].transcript
                
                # 清除之前的中間結果
                overwrite_chars = ' ' * (num_chars_printed - len(transcript))
                
                if not result.is_final:
                    # 中間結果 - 灰色顯示
                    print(f"\r\033[90m{transcript}{overwrite_chars}\033[0m", end='', flush=True)
                    num_chars_printed = len(transcript)
                else:
                    # 最終結果 - 綠色顯示
                    print(f"\r\033[92m✓ {transcript}\033[0m{overwrite_chars}")
                    
                    # 如果有檢測到的語言，顯示
                    if hasattr(result, 'language_code') and result.language_code:
                        print(f"  \033[94m[語言: {result.language_code}]\033[0m")
                    
                    num_chars_printed = 0
                    print("-" * 60)
                    
        except Exception as e:
            print(f"\n處理響應時出錯: {e}")


def main():
    if not PROJECT_ID:
        print("❌ 錯誤: 請設置 GOOGLE_CLOUD_PROJECT 環境變量")
        print("執行: export GOOGLE_CLOUD_PROJECT=your-project-id")
        return
    
    print("🎙️  實時語音轉文字 - Chirp 模型")
    print("=" * 60)
    print(f"📍 項目: {PROJECT_ID}")
    
    # 選擇語言模式
    print("\n🌍 語言設置:")
    print("1. 自動檢測 (推薦)")
    print("2. 中文")
    print("3. 英文")
    print("4. 日文")
    
    choice = input("\n請選擇 (1-4, 默認: 1): ").strip() or "1"
    
    language_map = {
        "1": "auto",
        "2": "zh-TW",
        "3": "en-US", 
        "4": "ja-JP"
    }
    
    language = language_map.get(choice, "auto")
    print(f"🗣️  語言設置: {language}")
    
    # 創建轉錄器
    transcriber = RealTimeTranscriber(language_code=language)
    
    # 開始轉錄
    transcriber.start_streaming()


if __name__ == "__main__":
    main() 