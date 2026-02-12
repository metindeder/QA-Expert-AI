import pandas as pd
import os

csv_path = "SmartBudget/data/transactions.csv"

def set_alternating_types():
    if not os.path.exists(csv_path):
        print(f"❌ Dosya bulunamadı: {csv_path}")
        return

    print(f"🔄 '{csv_path}' güncelleniyor...")
    
    try:
        # CSV'yi oku
        df = pd.read_csv(csv_path)
        
        # Matematiksel Mantık: Satır numarası çift ise Gelir, tek ise Gider
        # i % 2 == 0 (Çift) -> Gelir
        # i % 2 != 0 (Tek)  -> Gider
        df['type'] = ["Gelir" if i % 2 == 0 else "Gider" for i in range(len(df))]
        
        # Kaydet
        df.to_csv(csv_path, index=False)
        
        print("✅ İşlem Başarılı! Tüm satırlar 'Gelir - Gider' olarak sıralandı.")
        print("\n--- İlk 10 Satır Önizleme ---")
        print(df[['date', 'category', 'type', 'amount']].head(10))

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    set_alternating_types()