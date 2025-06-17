import os

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

def transcribe_chirp(
    audio_file: str,
) -> cloud_speech.RecognizeResponse:
    """Transcribes an audio file using the Chirp model of Google Cloud Speech-to-Text API.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
    Returns:
        cloud_speech.RecognizeResponse: The response from the Speech-to-Text API containing
        the transcription results.
    """
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint="us-central1-speech.googleapis.com",
        )
    )

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="chirp",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/us-central1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def transcribe_chirp_auto_detect_language(
    audio_file: str,
    region: str = "us-central1",
) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file and auto-detect spoken language using Chirp.
    Please see https://cloud.google.com/speech-to-text/v2/docs/encoding for more
    information on which audio encodings are supported.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
        region (str): The region for the API endpoint.
    Returns:
        cloud_speech.RecognizeResponse: The response containing the transcription results.
    """
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{region}-speech.googleapis.com",
        )
    )

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["auto"],  # Set language code to auto to detect language.
        model="chirp",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{region}/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
        print(f"Detected Language: {result.language_code}")

    return response


if __name__ == "__main__":
    # 檢查是否設置了項目 ID
    if not PROJECT_ID:
        print("錯誤: 請設置 GOOGLE_CLOUD_PROJECT 環境變量")
        print("執行: export GOOGLE_CLOUD_PROJECT=your-project-id")
        exit(1)
    
    # 測試音頻文件路徑
    audio_file = input("請輸入音頻文件路徑 (或按 Enter 使用默認測試): ").strip()
    
    if not audio_file:
        # 創建一個簡單的測試音頻文件
        print("沒有提供音頻文件，讓我們先檢查您是否有任何音頻文件...")
        print("支持的格式包括: .wav, .mp3, .flac, .m4a 等")
        print("如果您沒有音頻文件，您可以:")
        print("1. 使用您手機錄製一個短音頻")
        print("2. 下載網上的音頻樣本")
        print("3. 使用 macOS 內建的錄音功能")
        exit(0)
    
    if not os.path.exists(audio_file):
        print(f"錯誤: 找不到音頻文件 {audio_file}")
        exit(1)
    
    print(f"使用項目 ID: {PROJECT_ID}")
    print(f"轉錄音頻文件: {audio_file}")
    print("=" * 50)
    
    try:
        print("🎯 使用 Chirp 模型進行基本轉錄...")
        transcribe_chirp(audio_file)
        
        print("\n" + "=" * 50)
        
        print("🌍 使用 Chirp 模型進行語言自動檢測...")
        transcribe_chirp_auto_detect_language(audio_file)
        
    except Exception as e:
        print(f"錯誤: {e}")
        print("請確保:")
        print("1. 已正確設置 Google Cloud 認證")
        print("2. 項目中已啟用 Speech-to-Text API")
        print("3. 音頻文件格式受支持") 