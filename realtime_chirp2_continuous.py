#!/usr/bin/env python3
"""
🎙️ Google Cloud Speech-to-Text V2 連續實時轉錄
支持無限時長錄音，自動處理 5 分鐘流式限制
"""

import os
import sys
import json
import threading
import time
from queue import Queue
import pyaudio
import re
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

# 設置環境變量
os.environ['GOOGLE_CLOUD_PROJECT'] = 'lithe-window-713'

# 音頻參數
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms 緩衝
FORMAT = pyaudio.paInt16
CHANNELS = 1

# 顏色代碼
class Colors:
    GREY = '\033[90m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_custom_vocabulary():
    """載入自定義詞彙"""
    try:
        with open('custom_vocabulary.json', 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        
        phrases = []
        count = 0
        for category, terms in vocab_data.items():
            phrases.extend(terms)
            count += len(terms)
        
        print(f"📚 載入 {count} 個自定義詞彙")
        if count > 0:
            print(f"🚀 啟用詞彙適應性功能，提升專業術語識別準確度")
            print(f"📝 載入的詞彙包括:")
            # 顯示前 10 個詞彙
            displayed = phrases[:10]
            for term in displayed:
                print(f"   • {term}")
            if count > 10:
                print(f"   ... 還有 {count - 10} 個")
        
        return phrases
    except FileNotFoundError:
        print("📝 未找到自定義詞彙檔案，使用預設設定")
        return []
    except Exception as e:
        print(f"⚠️ 載入詞彙時出錯: {e}")
        return []

def fix_capitalization(text, custom_phrases):
    """修正文字中專有名詞的大小寫"""
    if not custom_phrases:
        return text
    
    result = text
    
    # 為每個自定義詞彙進行大小寫修正
    for phrase in custom_phrases:
        # 創建不區分大小寫的搜尋模式
        # 使用單詞邊界來確保完整匹配，但允許一些標點符號
        words = phrase.split()
        
        if len(words) == 1:
            # 單詞匹配：使用單詞邊界
            pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        else:
            # 多詞匹配：更靈活的匹配
            pattern = r'\b' + r'\s+'.join(re.escape(word.lower()) for word in words) + r'\b'
        
        def replace_func(match):
            return phrase  # 返回正確的大小寫版本
        
        # 不區分大小寫的替換
        result = re.sub(pattern, replace_func, result, flags=re.IGNORECASE)
    
    return result

class AudioStreamer:
    """音頻流處理器"""
    
    def __init__(self):
        self.audio_queue = Queue()
        self.should_stop = False
        self.stream = None
        self.audio_interface = None
        
    def start_recording(self):
        """開始錄音"""
        self.audio_interface = pyaudio.PyAudio()
        
        # 查找麥克風
        print("🎤 搜尋可用的麥克風...")
        for i in range(self.audio_interface.get_device_count()):
            info = self.audio_interface.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"   📱 {info['name']} (輸入聲道: {info['maxInputChannels']})")
        
        try:
            self.stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=self._audio_callback
            )
            
            device_info = self.audio_interface.get_device_info_by_index(self.stream._input_device_id)
            print(f"✅ 使用麥克風: {device_info['name']}")
            print(f"🎤 開始錄音...")
            
            self.stream.start_stream()
            return True
            
        except Exception as e:
            print(f"❌ 錄音失敗: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音頻回調函數"""
        if not self.should_stop:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def get_audio_generator(self):
        """音頻數據生成器"""
        while not self.should_stop:
            try:
                chunk = self.audio_queue.get(timeout=1.0)
                # 確保音頻塊大小不超過 25600 字節
                max_chunk_size = 25600
                if len(chunk) > max_chunk_size:
                    # 分割大塊
                    for i in range(0, len(chunk), max_chunk_size):
                        yield chunk[i:i + max_chunk_size]
                else:
                    yield chunk
            except:
                continue
    
    def stop_recording(self):
        """停止錄音"""
        self.should_stop = True
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio_interface:
            self.audio_interface.terminate()

class ContinuousTranscriber:
    """連續轉錄器 - 自動處理5分鐘限制"""
    
    def __init__(self):
        self.client = SpeechClient()
        self.audio_streamer = AudioStreamer()
        self.should_stop = False
        self.session_count = 0
        
    def create_recognition_config(self, phrases):
        """創建識別配置"""
        # 詞彙適應配置
        adaptation = None
        if phrases:
            phrase_set = cloud_speech.PhraseSet()
            for phrase in phrases:
                phrase_set.phrases.append(cloud_speech.PhraseSet.Phrase(value=phrase, boost=10.0))
            
            adaptation = cloud_speech.SpeechAdaptation()
            adaptation.phrase_sets.append(phrase_set)
        
        # 識別配置
        recognition_config = cloud_speech.RecognitionConfig(
            explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
                encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                audio_channel_count=CHANNELS,
            ),
            language_codes=["en-US"],  # 支持的語言
            model="chirp_2",
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
                max_alternatives=1,
            ),
        )
        
        if adaptation:
            recognition_config.adaptation = adaptation
            
        return recognition_config
    
    def single_stream_session(self, recognition_config):
        """單次流式會話（最多5分鐘）"""
        self.session_count += 1
        session_start_time = time.time()
        
        print(f"\n{Colors.CYAN}🔄 啟動會話 #{self.session_count}{Colors.END}")
        print(f"{Colors.YELLOW}⏱️ 此會話最多持續 5 分鐘{Colors.END}")
        
        # 流式識別配置
        streaming_config = cloud_speech.StreamingRecognitionConfig(
            config=recognition_config,
            streaming_features=cloud_speech.StreamingRecognitionFeatures(
                interim_results=True,
                voice_activity_timeout=cloud_speech.StreamingRecognitionFeatures.VoiceActivityTimeout(
                    speech_start_timeout=15,
                    speech_end_timeout=15,
                ),
            ),
        )
        
        def request_generator():
            """生成識別請求"""
            # 第一個請求包含配置
            yield cloud_speech.StreamingRecognizeRequest(
                recognizer=f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/locations/us-central1/recognizers/_",
                streaming_config=streaming_config,
            )
            
            # 後續請求包含音頻數據
            for chunk in self.audio_streamer.get_audio_generator():
                if self.should_stop:
                    break
                    
                # 檢查是否接近5分鐘限制
                if time.time() - session_start_time > 280:  # 4分40秒
                    print(f"\n{Colors.YELLOW}⚠️ 接近5分鐘限制，準備重新連接...{Colors.END}")
                    break
                    
                yield cloud_speech.StreamingRecognizeRequest(audio=chunk)
        
        try:
            responses = self.client.streaming_recognize(requests=request_generator())
            self.process_responses(responses)
            
        except Exception as e:
            if "Max duration of 5 minutes" in str(e):
                print(f"\n{Colors.YELLOW}⏱️ 會話 #{self.session_count} 達到5分鐘限制{Colors.END}")
            else:
                print(f"\n{Colors.RED}❌ 會話 #{self.session_count} 錯誤: {e}{Colors.END}")
    
    def process_responses(self, responses):
        """處理識別響應"""
        last_interim_length = 0
        
        # 載入詞彙用於大小寫修正
        custom_phrases = load_custom_vocabulary()
        
        try:
            for response in responses:
                if self.should_stop:
                    break
                    
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript.strip()
                        
                        if result.is_final:
                            # 最終結果 - 綠色，先修正大小寫再顯示
                            corrected_transcript = fix_capitalization(transcript, custom_phrases)
                            
                            clear_chars = max(0, last_interim_length - len(corrected_transcript) - 3)
                            overwrite_chars = " " * clear_chars
                            
                            print(f"\r{Colors.GREEN}✅ {corrected_transcript}{Colors.END}{overwrite_chars}")
                            print("-" * 60)
                            last_interim_length = 0
                        else:
                            # 中間結果 - 灰色，覆蓋之前的內容
                            # 計算需要清除的字符數量
                            clear_chars = max(0, last_interim_length - len(transcript) - 3)
                            overwrite_chars = " " * clear_chars
                            
                            print(f"\r{Colors.GREY}🔘 {transcript}{Colors.END}{overwrite_chars}", end='', flush=True)
                            
                            # 記錄當前行的長度（包括emoji和前綴）
                            last_interim_length = len(transcript) + 3
                            
        except Exception as e:
            if "Max duration of 5 minutes" not in str(e):
                print(f"\n{Colors.RED}❌ 處理響應錯誤: {e}{Colors.END}")
    
    def start_continuous_transcription(self):
        """開始連續轉錄"""
        print(f"{Colors.BOLD}{Colors.BLUE}🎙️  Google Cloud Speech-to-Text V2 連續實時轉錄{Colors.END}")
        print("=" * 60)
        print(f"📍 項目: {os.environ['GOOGLE_CLOUD_PROJECT']}")
        print(f"🚀 使用 Chirp 2 模型進行連續語音識別")
        print(f"⏱️ 自動處理 5 分鐘流式限制")
        print(f"📝 按 Ctrl+C 停止")
        print("=" * 60)
        
        # 載入自定義詞彙
        phrases = load_custom_vocabulary()
        recognition_config = self.create_recognition_config(phrases)
        
        # 開始錄音
        if not self.audio_streamer.start_recording():
            return
        
        print(f"✅ 連接成功，開始連續轉錄:")
        print("-" * 60)
        print(f"💡 說話提示:")
        print(f"   🔘 灰色 = 正在識別")
        print(f"   ✅ 綠色 = 確認結果")
        print(f"   🔄 藍色 = 會話重連")
        print("-" * 60)
        
        try:
            while not self.should_stop:
                # 啟動新的5分鐘會話
                self.single_stream_session(recognition_config)
                
                if not self.should_stop:
                    print(f"\n{Colors.CYAN}🔄 自動重新連接... (會話 #{self.session_count + 1}){Colors.END}")
                    time.sleep(1)  # 短暫延遲
                    
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⏹️ 用戶停止轉錄{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ 轉錄錯誤: {e}{Colors.END}")
        finally:
            self.stop()
    
    def stop(self):
        """停止轉錄"""
        self.should_stop = True
        self.audio_streamer.stop_recording()
        print(f"\n{Colors.GREEN}✅ 轉錄已停止{Colors.END}")
        print(f"📊 總會話數: {self.session_count}")

def main():
    """主函數"""
    try:
        transcriber = ContinuousTranscriber()
        transcriber.start_continuous_transcription()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 再見！{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ 應用程序錯誤: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main() 