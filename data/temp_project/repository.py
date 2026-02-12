import pandas as pd
import os

class TransactionRepository:
    def __init__(self, csv_filename="transactions.csv"):
        # Projenin ana dizinini dinamik olarak bul
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.csv_path = os.path.join(base_dir, "data", csv_filename)
        self._initialize_csv()

    def _initialize_csv(self):
        """CSV dosyası ve klasörü yoksa oluşturur."""
        folder = os.path.dirname(self.csv_path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        if not os.path.exists(self.csv_path):
            df = pd.DataFrame(columns=["date", "type", "category", "amount", "description"])
            df.to_csv(self.csv_path, index=False)

    def get_all_transactions(self):
        """Tüm veriyi okur."""
        if os.path.exists(self.csv_path):
            try:
                df = pd.read_csv(self.csv_path)
                return df
            except:
                pass
        return pd.DataFrame(columns=["date", "type", "category", "amount", "description"])

    def add_transaction(self, new_data: dict):
        """Yeni veri ekler."""
        try:
            df = self.get_all_transactions()
            new_row = pd.DataFrame([new_data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.csv_path, index=False)
            return True
        except Exception as e:
            print(f"Ekleme hatası: {e}")
            return False

    def delete_transaction(self, index):
        """Belirtilen index'teki satırı siler."""
        try:
            df = self.get_all_transactions()
            if index in df.index:
                df = df.drop(index)
                df.to_csv(self.csv_path, index=False)
                return True
            return False
        except Exception as e:
            print(f"Silme hatası: {e}")
            return False

    def get_financial_summary(self):
        """AI ve Dashboard için özet hesaplar."""
        df = self.get_all_transactions()
        if df.empty:
            return {"total_income": 0, "total_expense": 0, "balance": 0, "top_expense_category": "Veri Yok"}

        # Veri temizliği: Stringleri düzelt, sayıları garantiye al
        df['type'] = df['type'].astype(str).str.capitalize().str.strip()
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        total_income = df[df["type"] == "Gelir"]["amount"].sum()
        total_expense = df[df["type"] == "Gider"]["amount"].sum()
        
        # En çok harcanan kategori
        expenses = df[df["type"] == "Gider"]
        if not expenses.empty:
            top_cat = expenses.groupby("category")["amount"].sum().idxmax()
            top_amount = expenses.groupby("category")["amount"].sum().max()
            top_cat_text = f"{top_cat} ({top_amount:,.0f} TL)"
        else:
            top_cat_text = "Harcama Yok"

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "top_expense_category": top_cat_text
        }