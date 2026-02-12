import requests
import json

class LLMClient:
    def __init__(self, model_name="qa-expert"):
        """
        Ollama API Client.
        Modelfile ile ozellestirilmis 'QA Expert' modeli ile konusur.
        """
        self.api_url = "http://localhost:11434/api/generate"
        # Senin olusturdugun ozel modelin adi (ollama create ile verdigin isim)
        self.model = model_name

    def generate_response(self, context_data, metadata, user_query):
        """
        RAG'dan gelen veriyi (Gereksinim veya Kod) modele iletir.
        Model zaten 'System Prompt' icerdigi icin burada tekrar rol tanimlamiyoruz.
        """
        
        # 1. Girdiyi Hazirla (Data Formatting)
        # Modelfile'daki {{ .Prompt }} kismina denk gelecek yapi.
        # Hem kod hem metin gereksinimleri icin evrensel format.
        prompt_payload = f"""
        CONTEXT / INPUT DATA:
        {context_data}
        
        STRUCTURAL DEPENDENCIES (Graph/Metadata):
        {metadata}
        
        USER SPECIFIC REQUEST:
        {user_query}
        """

        # 2. Ollama'ya Istek Gonder
        # System prompt'u gondermiyoruz, cunku Modelfile icinde zaten gomulu!
        payload = {
            "model": self.model,
            "prompt": prompt_payload,
            "stream": False,
            "options": {
                # Modelfile'da 0.1 tanimli ama burasi override eder. 
                # Gherkin gibi kati formatlar icin dusuk sicaklik iyidir.
                "temperature": 0.1, 
                "num_ctx": 4096
            }
        }

        try:
            print(f"Sending request to Custom Model ({self.model})...")
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result['response']
            
        except requests.exceptions.ConnectionError:
            return "Hata: Ollama baglantisi kurulamadi. 'ollama serve' calisiyor mu?"
        except Exception as e:
            return f"Model uretim hatasi: {str(e)}"