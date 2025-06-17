#!/usr/bin/env python3
"""
自定義詞彙管理工具
用於管理語音識別的專業術語詞庫
"""

import json
import os
from datetime import datetime

VOCABULARY_FILE = "custom_vocabulary.json"

def load_vocabulary():
    """載入自定義詞彙"""
    if os.path.exists(VOCABULARY_FILE):
        with open(VOCABULARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "phrases": [],
        "categories": {},
        "last_updated": None
    }

def save_vocabulary(vocab_data):
    """儲存自定義詞彙"""
    vocab_data["last_updated"] = datetime.now().isoformat()
    with open(VOCABULARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(vocab_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 詞彙已儲存到 {VOCABULARY_FILE}")

def add_phrase(vocab_data, phrase, category=None):
    """新增詞彙"""
    if phrase not in vocab_data["phrases"]:
        vocab_data["phrases"].append(phrase)
        if category:
            if category not in vocab_data["categories"]:
                vocab_data["categories"][category] = []
            if phrase not in vocab_data["categories"][category]:
                vocab_data["categories"][category].append(phrase)
        print(f"✅ 已新增: {phrase}")
        if category:
            print(f"   分類: {category}")
    else:
        print(f"⚠️  詞彙已存在: {phrase}")

def remove_phrase(vocab_data, phrase):
    """移除詞彙"""
    if phrase in vocab_data["phrases"]:
        vocab_data["phrases"].remove(phrase)
        # 從分類中移除
        for category in vocab_data["categories"]:
            if phrase in vocab_data["categories"][category]:
                vocab_data["categories"][category].remove(phrase)
        print(f"✅ 已移除: {phrase}")
    else:
        print(f"❌ 詞彙不存在: {phrase}")

def list_vocabulary(vocab_data):
    """顯示所有詞彙"""
    print("\n📚 自定義詞彙庫:")
    print("=" * 50)
    
    if not vocab_data["phrases"]:
        print("❌ 詞彙庫為空")
        return
    
    print(f"📊 總共 {len(vocab_data['phrases'])} 個詞彙")
    if vocab_data["last_updated"]:
        print(f"🕒 最後更新: {vocab_data['last_updated']}")
    print()
    
    # 按分類顯示
    if vocab_data["categories"]:
        for category, phrases in vocab_data["categories"].items():
            if phrases:
                print(f"📁 {category}:")
                for phrase in phrases:
                    print(f"   • {phrase}")
                print()
    
    # 顯示未分類的詞彙
    categorized_phrases = set()
    for phrases in vocab_data["categories"].values():
        categorized_phrases.update(phrases)
    
    uncategorized = [p for p in vocab_data["phrases"] if p not in categorized_phrases]
    if uncategorized:
        print("📁 未分類:")
        for phrase in uncategorized:
            print(f"   • {phrase}")

def add_predefined_phrases(vocab_data):
    """新增一些常見的專業術語範例"""
    # 技術相關
    tech_phrases = [
        "API", "SDK", "REST API", "GraphQL", "OAuth", "JWT",
        "Docker", "Kubernetes", "microservices", "DevOps",
        "machine learning", "artificial intelligence", "neural network",
        "deep learning", "computer vision", "natural language processing",
        "TensorFlow", "PyTorch", "scikit-learn", "pandas", "NumPy"
    ]
    
    # 商業相關
    business_phrases = [
        "KPI", "ROI", "SaaS", "B2B", "B2C", "CRM", "ERP",
        "scalability", "monetization", "MVP", "proof of concept",
        "user experience", "user interface", "agile development"
    ]
    
    # Google Cloud 相關
    gcp_phrases = [
        "Google Cloud", "BigQuery", "Cloud Storage", "Cloud Run",
        "App Engine", "Compute Engine", "Cloud Functions",
        "Firestore", "Cloud SQL", "Pub Sub", "Cloud Vision",
        "Speech to Text", "Cloud Translation"
    ]
    
    print("📦 新增預設專業術語...")
    
    for phrase in tech_phrases:
        add_phrase(vocab_data, phrase, "技術")
    
    for phrase in business_phrases:
        add_phrase(vocab_data, phrase, "商業")
        
    for phrase in gcp_phrases:
        add_phrase(vocab_data, phrase, "Google Cloud")
    
    print(f"✅ 已新增 {len(tech_phrases + business_phrases + gcp_phrases)} 個預設術語")

def interactive_mode():
    """互動模式"""
    vocab_data = load_vocabulary()
    
    while True:
        print("\n🎯 自定義詞彙管理")
        print("=" * 30)
        print("1. 📝 新增詞彙")
        print("2. 🗑️  移除詞彙") 
        print("3. 📚 查看詞彙庫")
        print("4. 📦 新增預設術語")
        print("5. 📤 匯出詞彙")
        print("6. 📥 匯入詞彙")
        print("7. 🚀 測試識別")
        print("0. 退出")
        
        choice = input("\n請選擇 (0-7): ").strip()
        
        if choice == "1":
            phrase = input("輸入詞彙: ").strip()
            if phrase:
                category = input("輸入分類 (可選): ").strip() or None
                add_phrase(vocab_data, phrase, category)
                save_vocabulary(vocab_data)
        
        elif choice == "2":
            phrase = input("輸入要移除的詞彙: ").strip()
            if phrase:
                remove_phrase(vocab_data, phrase)
                save_vocabulary(vocab_data)
        
        elif choice == "3":
            list_vocabulary(vocab_data)
        
        elif choice == "4":
            add_predefined_phrases(vocab_data)
            save_vocabulary(vocab_data)
        
        elif choice == "5":
            export_file = input("匯出檔名 (預設: vocabulary_export.txt): ").strip() or "vocabulary_export.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                for phrase in vocab_data["phrases"]:
                    f.write(phrase + "\n")
            print(f"✅ 已匯出到 {export_file}")
        
        elif choice == "6":
            import_file = input("匯入檔名: ").strip()
            if os.path.exists(import_file):
                with open(import_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for line in lines:
                    phrase = line.strip()
                    if phrase:
                        add_phrase(vocab_data, phrase)
                save_vocabulary(vocab_data)
            else:
                print("❌ 檔案不存在")
        
        elif choice == "7":
            print("🚀 啟動帶自定義詞彙的語音識別...")
            break
        
        elif choice == "0":
            break
        
        else:
            print("❌ 無效選擇")

def get_phrases_for_recognition():
    """獲取用於語音識別的詞彙列表"""
    vocab_data = load_vocabulary()
    return vocab_data["phrases"]

if __name__ == "__main__":
    interactive_mode() 