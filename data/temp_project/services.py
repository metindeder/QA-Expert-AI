import pandas as pd
from core.repository import TransactionRepository
from datetime import datetime

class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()

    def _get_clean_df(self):
        df = self.repo.get_all_transactions()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            df['type'] = df['type'].astype(str).str.capitalize().str.strip()
        return df

    def add_entry(self, type_, category, amount, description):
        current_date = datetime.now().strftime("%Y-%m-%d")
        new_data = {
            "date": current_date,
            "type": type_,
            "category": category,
            "amount": amount,
            "description": description
        }
        self.repo.add_transaction(new_data)

    def delete_entry(self, index):
        return self.repo.delete_transaction(index)

    def get_current_month_data(self):
        df = self._get_clean_df()
        if df.empty: return df
        now = datetime.now()
        mask = (df['date'].dt.year == now.year) & (df['date'].dt.month == now.month)
        return df[mask].sort_values(by="date", ascending=False)

    def get_summary(self):
        return self.repo.get_financial_summary()

    def get_monthly_expenses(self, year, month):
        df = self._get_clean_df()
        if df.empty: return pd.Series()
        mask = (df['date'].dt.year == year) & (df['date'].dt.month == month) & (df['type'] == 'Gider')
        filtered_df = df[mask]
        if filtered_df.empty: return pd.Series()
        return filtered_df.groupby("category")["amount"].sum()

    def get_yearly_trend(self, year):
        df = self._get_clean_df()
        if df.empty: return pd.DataFrame()
        mask = (df['date'].dt.year == year)
        df_year = df[mask]
        if df_year.empty: return pd.DataFrame()
        trend = df_year.groupby([df_year['date'].dt.month_name(), 'type'])['amount'].sum().unstack().fillna(0)
        months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        return trend.reindex([m for m in months_order if m in trend.index])

    # --- EKLENEN YENİ FONKSİYON ---
    def get_monthly_category_breakdown(self):
        """AI için bu ayın harcama detaylarını metne çevirir."""
        df = self.get_current_month_data()
        
        if df.empty:
            return "Bu ay henüz veri yok."
            
        # Sadece Giderleri al
        expenses = df[df['type'] == 'Gider']
        
        if expenses.empty:
            return "Bu ay henüz gider yok."
            
        # Kategoriye göre topla
        breakdown = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
        
        # Metin listesi oluştur
        text_list = [f"{cat}: {amt:,.0f} TL" for cat, amt in breakdown.items()]
        
        return ", ".join(text_list)