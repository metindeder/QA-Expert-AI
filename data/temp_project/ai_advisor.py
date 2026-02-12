import os
from llama_cpp import Llama

class AIAdvisor:
    def __init__(self, model_filename="qwen2.5-1.5b-instruct-q4_k_m.gguf"):
        # Dosya yolunu bul
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)
        model_path = os.path.join(base_dir, "models", model_filename)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model bulunamadı: {model_path}")

        print(f"🤖 AI Model Yükleniyor... ({model_filename})")
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_gpu_layers=-1, 
                verbose=False
            )
            print("✅ Model hazır!")
        except Exception as e:
            print(f"❌ Model hatası: {e}")
            self.llm = None

    # --- BURASI DEĞİŞTİ: ARTIK 2 PARAMETRE ALIYOR ---
    def ask_for_advice(self, financial_summary: dict, monthly_breakdown: str):
        
        if not self.llm:
            return "⚠️ Model yüklenemediği için tavsiye verilemiyor."

        # RAG (Context) Oluşturma
        context_text = f"""
        GENEL DURUM:
        - Toplam Gelir: {financial_summary.get('total_income', 0)} TL
        - Toplam Gider: {financial_summary.get('total_expense', 0)} TL
        - Net Bakiye: {financial_summary.get('balance', 0)} TL
        
        BU AYIN HARCAMA DETAYLARI:
        {monthly_breakdown}
        """

        # Prompt Hazırlama
        prompt = f"""<|im_start|>system
Sen finansal bir danışmansın. Kullanıcının bu ayki harcama detaylarına bakarak ona özel, kısa ve madde işaretli tasarruf tavsiyeleri ver.<|im_end|>
<|im_start|>user
Verilerim:
{context_text}

Bütçemi düzeltmek için 3 somut öneri ver.<|im_end|>
<|im_start|>assistant
"""

        try:
            output = self.llm(
                prompt,
                max_tokens=500,
                temperature=0.7,
                stop=["<|im_end|>", "User:"]
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"⚠️ Hata: {e}"