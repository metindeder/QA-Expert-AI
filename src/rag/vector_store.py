import os
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class CodeVectorStore:
    def __init__(self, collection_name="qa_expert_codebase"):
        """
        Graph-Enhanced Vector Store.
        Kodları hem anlamsal (vector) hem de yapısal (graph metadata) olarak saklar.
        """
        # Veritabanını diske kaydetmek için yol belirle
        self.db_path = os.path.join(os.getcwd(), "data", "vector_db")
        
        # ChromaDB İstemcisini (Client) başlat
        # PersistentClient, verilerin program kapansa bile silinmemesini sağlar.
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Embedding Modeli (Kodlar ve İngilizce için optimize edilmiş model)
        # 'all-MiniLM-L6-v2' hem hızlıdır hem de CPU dostudur.
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Koleksiyonu oluştur veya varsa getir
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_graph_documents(self, graph):
        """
        NetworkX Grafiğindeki düğümleri Vektör Veritabanına aktarır.
        NOVELTY: Düğümleri kaydederken 'outgoing_edges' (çağırdığı fonksiyonlar) bilgisini de ekler.
        """
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        print(f"Updating database... Total Nodes in Graph: {graph.number_of_nodes()}")

        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            
            # Sadece dosya içeriği veya fonksiyon kodu olanları al
            # Parser'dan gelen veriye göre 'content' veya 'code' anahtarını kontrol et
            content = node_data.get("content") or node_data.get("code")
            
            if content:
                # 1. Bağımlılıkları Bul (Graph Traversal)
                # Bu düğümden çıkan okları (çağırdığı fonksiyonları) bul
                # graph.out_edges(node_id) bize (Kaynak, Hedef) çiftlerini verir
                neighbors = [target for _, target in graph.out_edges(node_id)]
                neighbor_str = ",".join(neighbors)

                # 2. Metadata Hazırla (Novelty Kısmı Burası)
                # ChromaDB metadata içinde listeleri doğrudan tutamaz, string'e çevirdik.
                meta = {
                    "type": node_data.get("type", "unknown"),
                    "node_id": node_id,
                    "calls": neighbor_str  # Bu fonksiyonun kimi çağırdığını metadata olarak ekle
                }
                
                # 3. Embedding Hesapla (Metni vektöre çevir)
                vector = self.embedding_model.encode(content).tolist()

                # Listelere ekle (Batch işlem için)
                ids.append(str(uuid.uuid4()))
                documents.append(content)
                metadatas.append(meta)
                embeddings.append(vector)

        # Hepsini tek seferde ChromaDB'ye ekle
        if documents:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            print(f"Success: {len(documents)} code snippets and Graph Metadata processed into Vector DB.")
        else:
            print("Warning: No suitable documents found in the graph to add.")

    def search_similar(self, query, k=3):
        """
        Kullanıcı sorgusuna en uygun kod parçalarını getirir.
        """
        # Sorguyu vektöre çevir
        query_vector = self.embedding_model.encode(query).tolist()
        
        # Veritabanında en yakın vektörleri ara
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )
        
        return results