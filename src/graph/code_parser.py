import os
import networkx as nx
from tree_sitter import Language, Parser
import tree_sitter_python

class CodeGraphParser:
    def __init__(self):
        """
        Neuro-Symbolic Graph Parser.
        Kodu metin olarak degil, AST (Abstract Syntax Tree) olarak analiz eder.
        """
        try:
            # HATA DUZELTME:
            # tree-sitter guncel surumlerinde (0.22+) Language sinifi hem pointer hem de isim ister.
            # tree_sitter_python.language() pointer'i verir, "python" ise ismidir.
            ptr = tree_sitter_python.language()
            self.PY_LANGUAGE = Language(ptr, "python")
            
            self.parser = Parser()
            self.parser.set_language(self.PY_LANGUAGE)
            
        except Exception as e:
            print(f"An error occurred while loading the language: {e}")
            # Alternatif yukleme denemesi (Eski surumler icin)
            try:
                self.PY_LANGUAGE = Language(tree_sitter_python.language())
                self.parser = Parser()
                self.parser.set_language(self.PY_LANGUAGE)
                print("Installed with backward compatibility.")
            except:
                raise e
            
        self.graph = nx.DiGraph()  # Yonlu Grafik (Directed Graph)

    def parse_file(self, file_path):
        """Bir dosyadaki tum Class, Fonksiyon ve Cagrilari grafige ekler."""
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Kodun byte formatina cevrilmesi
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        
        # Dosya dugumu ekle
        file_node_id = f"FILE:{os.path.basename(file_path)}"
        self.graph.add_node(file_node_id, type="file", content=code)

        # 1. Tanimlari Bul (Definition Extraction)
        self._extract_definitions(root_node, file_node_id, code.encode("utf8"))
        
        # 2. Cagrilari Bul (Call Graph Construction)
        self._extract_calls(root_node, file_node_id, code.encode("utf8"))

        print(f"Parsed: {os.path.basename(file_path)} | Nodes: {self.graph.number_of_nodes()} | Edges: {self.graph.number_of_edges()}")

    def _extract_definitions(self, node, parent_id, code_bytes):
        """Fonksiyon ve Class tanimlarini bulur."""
        # Recursive (Ozyinelemeli) arama
        for child in node.children:
            if child.type == "function_definition":
                func_name = self._get_node_name(child, code_bytes)
                node_id = f"FUNC:{func_name}"
                
                # Grafige ekle
                code_snippet = self._get_code_snippet(child, code_bytes)
                self.graph.add_node(node_id, type="function", code=code_snippet)
                self.graph.add_edge(parent_id, node_id, relation="defines")
                
                # Icindeki tanimlari da ara (Nested functions)
                self._extract_definitions(child, node_id, code_bytes)

            elif child.type == "class_definition":
                class_name = self._get_node_name(child, code_bytes)
                node_id = f"CLASS:{class_name}"
                
                code_snippet = self._get_code_snippet(child, code_bytes)
                self.graph.add_node(node_id, type="class", code=code_snippet)
                self.graph.add_edge(parent_id, node_id, relation="defines")
                
                self._extract_definitions(child, node_id, code_bytes)
            
            else:
                self._extract_definitions(child, parent_id, code_bytes)

    def _extract_calls(self, node, scope_id, code_bytes):
        """Kod icindeki fonksiyon cagrilarini (Calls) yakalar."""
        for child in node.children:
            if child.type == "call":
                # Cagrilan fonksiyonun adini bul
                func_node = child.child_by_field_name("function")
                if func_node:
                    called_func = self._get_text(func_node, code_bytes)
                    target_id = f"FUNC:{called_func}"
                    
                    # Eger cagrilan fonksiyon grafikte varsa kenar (edge) ciz
                    self.graph.add_edge(scope_id, target_id, relation="calls")
            
            self._extract_calls(child, scope_id, code_bytes)

    def _get_node_name(self, node, code_bytes):
        """AST dugumunun ismini (identifier) ceker."""
        name_node = node.child_by_field_name("name")
        return self._get_text(name_node, code_bytes) if name_node else "anon"

    def _get_text(self, node, code_bytes):
        """Byte kodunu string'e cevirir."""
        return code_bytes[node.start_byte : node.end_byte].decode("utf8")

    def _get_code_snippet(self, node, code_bytes):
        """Fonksiyonun tum kod blogunu alir."""
        return code_bytes[node.start_byte : node.end_byte].decode("utf8")

    def save_graph(self, path="data/graph_db/project_graph.gml"):
        """Grafigi diske kaydeder."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        nx.write_gml(self.graph, path)
        print(f"Graph saved: {path}")

# --- Test Alani ---
if __name__ == "__main__":
    dummy_code = """
class Auth:
    def login(self, user, password):
        if self.check_db(user):
            return True
        return False

    def check_db(self, user):
        print("Checking DB...")
        return True

def main():
    auth = Auth()
    auth.login("user", "1234")
"""
    test_file = "temp_test.py"
    with open(test_file, "w") as f:
        f.write(dummy_code)

    try:
        parser = CodeGraphParser()
        parser.parse_file(test_file)
        
        print("\n--- Graphic Nodes ---")
        print(parser.graph.nodes)
        print("\n--- Graphic Relationships ---")
        print(parser.graph.edges)
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)