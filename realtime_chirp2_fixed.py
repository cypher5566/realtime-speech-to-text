#!/usr/bin/env python3
"""
Google Cloud Speech-to-Text V2 實時轉錄
基於官方文檔重新實現
"""

import os
import queue
import sys
import threading
import time

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import pyaudio
from custom_vocabulary import get_phrases_for_recognition
import re

# 音頻參數
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

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

class MicrophoneStream:
    """麥克風音頻流類"""
    
    def __init__(self, rate=RATE, chunk=CHUNK):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """將音頻數據放入緩衝區"""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """音頻數據生成器 - 限制音頻塊大小"""
        MAX_CHUNK_SIZE = 25600  # Google Cloud 限制 (25KB)
        
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            
            # 直接發送單個塊，避免累積過多數據
            if len(chunk) <= MAX_CHUNK_SIZE:
                yield chunk
            else:
                # 如果單個塊太大，分割它
                for i in range(0, len(chunk), MAX_CHUNK_SIZE):
                    yield chunk[i:i+MAX_CHUNK_SIZE]


def transcribe_streaming_v2():
    """使用 Speech v2 進行實時轉錄"""
    print("🎙️  Google Cloud Speech-to-Text V2 實時轉錄")
    print("=" * 60)
    print(f"📍 項目: {PROJECT_ID}")
    print("🚀 使用 Chirp 2 模型進行實時語音識別")
    print("📝 按 Ctrl+C 停止")
    print("=" * 60)

    # 創建客戶端
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint="us-central1-speech.googleapis.com",
        )
    )

    # 載入自定義詞彙
    custom_phrases = get_phrases_for_recognition()
    
    # 配置識別 - 明確指定編碼格式
    recognition_config = cloud_speech.RecognitionConfig(
        explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
            encoding=cloud_speech.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            audio_channel_count=1,
        ),
        language_codes=["en-US"],  # 使用英文
        model="chirp_2",
    )
    
    # 如果有自定義詞彙，加入 Speech v2 適應性配置
    if custom_phrases:
        print(f"📚 載入 {len(custom_phrases)} 個自定義詞彙")
        print("🚀 啟用詞彙適應性功能，提升專業術語識別準確度")
        
        # 顯示前10個詞彙
        print("📝 載入的詞彙包括:")
        for i, phrase in enumerate(custom_phrases[:10]):
            print(f"   • {phrase}")
        if len(custom_phrases) > 10:
            print(f"   ... 還有 {len(custom_phrases) - 10} 個")
        
        # 使用 Speech v2 的正確適應性格式
        phrase_set = cloud_speech.PhraseSet(
            phrases=[
                {"value": phrase, "boost": 10.0}
                for phrase in custom_phrases[:100]  # 限制數量避免超限
            ]
        )
        
        recognition_config.adaptation = cloud_speech.SpeechAdaptation(
            phrase_sets=[
                cloud_speech.SpeechAdaptation.AdaptationPhraseSet(
                    inline_phrase_set=phrase_set
                )
            ]
        )

    # 流式配置
    streaming_config = cloud_speech.StreamingRecognitionConfig(
        config=recognition_config,
        streaming_features=cloud_speech.StreamingRecognitionFeatures(
            interim_results=True,  # 啟用中間結果
        )
    )

    # 創建初始請求
    config_request = cloud_speech.StreamingRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
        streaming_config=streaming_config,
    )

    def requests_generator(config_request, audio_generator):
        """請求生成器 - 按照官方文檔格式"""
        yield config_request
        for audio_chunk in audio_generator:
            yield cloud_speech.StreamingRecognizeRequest(audio=audio_chunk)

    print("🎤 開始錄音...")
    
    try:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            
            requests = requests_generator(config_request, audio_generator)
            
            # 開始流式識別
            responses = client.streaming_recognize(requests=requests)
            
            print("✅ 連接成功，開始實時轉錄:")
            print("-" * 60)
            print("💡 說話提示:")
            print("   🔘 灰色 = 正在識別")
            print("   ✅ 綠色 = 確認結果")
            print("-" * 60)
            
            listen_print_loop(responses)
            
    except KeyboardInterrupt:
        print("\n\n🛑 用戶停止錄音")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


def listen_print_loop(responses):
    """處理並顯示轉錄結果"""
    last_interim_length = 0
    
    # 載入詞彙用於大小寫修正
    custom_phrases = get_phrases_for_recognition()
    
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript.strip()

        if not result.is_final:
            # 中間結果 - 灰色，覆蓋之前的內容
            # 計算需要清除的字符數量
            clear_chars = max(0, last_interim_length - len(transcript) - 3)
            overwrite_chars = " " * clear_chars
            
            sys.stdout.write(f"\r🔘 \033[90m{transcript}\033[0m{overwrite_chars}")
            sys.stdout.flush()
            
            # 記錄當前行的長度（包括emoji和前綴）
            last_interim_length = len(transcript) + 3
        else:
            # 最終結果 - 綠色，先修正大小寫再顯示
            corrected_transcript = fix_capitalization(transcript, custom_phrases)
            
            clear_chars = max(0, last_interim_length - len(corrected_transcript) - 3)
            overwrite_chars = " " * clear_chars
            
            print(f"\r✅ \033[92m{corrected_transcript}\033[0m{overwrite_chars}")
            print("-" * 60)
            last_interim_length = 0

            # 檢查退出關鍵字
            if any(word in transcript.lower() for word in ["exit", "quit", "stop"]):
                print("👋 檢測到退出指令，停止轉錄")
                break


def main():
    if not PROJECT_ID:
        print("❌ 錯誤: 請設置 GOOGLE_CLOUD_PROJECT 環境變量")
        print("執行: export GOOGLE_CLOUD_PROJECT=your-project-id")
        return

    transcribe_streaming_v2()


if __name__ == "__main__":
    main() 