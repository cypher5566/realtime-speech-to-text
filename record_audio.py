#!/usr/bin/env python3
"""
簡單的音頻錄製腳本，使用 macOS 的 afrecord 功能
"""

import subprocess
import sys
import os
from datetime import datetime

def record_audio(output_file="test_audio.wav", duration=10):
    """
    使用 macOS 內建的 afrecord 錄製音頻
    
    Args:
        output_file (str): 輸出音頻文件名
        duration (int): 錄製時長（秒）
    """
    
    print(f"🎤 準備錄製音頻...")
    print(f"📁 文件名: {output_file}")
    print(f"⏱️  錄製時長: {duration} 秒")
    print("請準備好說話，3秒後開始錄製...")
    
    # 倒數計時
    import time
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("🔴 開始錄製！請說話...")
    
    try:
        # 使用 afrecord 命令錄製音頻
        # -f 指定格式，-c 指定聲道數，-r 指定採樣率，-t 指定時長
        cmd = [
            "afrecord",
            "-f", "WAVE",  # WAV 格式
            "-c", "1",     # 單聲道
            "-r", "16000", # 16kHz 採樣率（適合語音識別）
            "-t", str(duration),  # 錄製時長
            output_file
        ]
        
        subprocess.run(cmd, check=True)
        print(f"✅ 錄製完成！音頻已保存到: {output_file}")
        
        # 檢查文件大小
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"📊 文件大小: {file_size} bytes")
            return output_file
        else:
            print("❌ 錄製失敗：找不到輸出文件")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 錄製失敗: {e}")
        print("請確保您使用的是 macOS 系統")
        return None
    except FileNotFoundError:
        print("❌ 找不到 afrecord 命令")
        print("請確保您使用的是 macOS 系統")
        return None

def main():
    print("🎙️  音頻錄製工具")
    print("=" * 40)
    
    # 獲取用戶輸入
    output_file = input("輸入音頻文件名 (默認: test_audio.wav): ").strip()
    if not output_file:
        output_file = "test_audio.wav"
    
    try:
        duration = int(input("錄製時長（秒，默認: 10）: ") or 10)
    except ValueError:
        duration = 10
    
    # 錄製音頻
    recorded_file = record_audio(output_file, duration)
    
    if recorded_file:
        print(f"\n🚀 現在您可以使用以下命令測試 Chirp:")
        print(f"python chirp_transcribe.py")
        print(f"然後輸入音頻文件路徑: {recorded_file}")

if __name__ == "__main__":
    main() 