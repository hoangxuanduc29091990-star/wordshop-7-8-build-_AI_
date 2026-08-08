import os
try:
    import chromadb
except Exception:
    chromadb = None
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None
try:
    from google import genai
except Exception:
    genai = None

# Xác định đường dẫn thư mục data tuyệt đối
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
DEFAULT_PDF_PATH = os.path.join(ROOT_DIR, "data", "company_policy.pdf")

class RAGEngine:
    def __init__(self, pdf_path: str = DEFAULT_PDF_PATH):
        if chromadb is None:
            print("[RAG Warning] Package 'chromadb' không được cài; bỏ qua nạp RAG.")
            self.chroma_client = None
            self.collection = None
            self.pdf_path = pdf_path
            self.client = None
            return

        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(name="internal_knowledge")
        self.pdf_path = pdf_path

        if genai is None:
            print("[RAG Warning] Package 'google-genai' không được cài; bỏ qua nạp embeddings.")
            self.client = None
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

        self._initialize_db()

    def _initialize_db(self):
        if not os.path.exists(self.pdf_path):
            print(f"[RAG Warning] File {self.pdf_path} chưa tồn tại. Bỏ qua nạp RAG.")
            return

        print(f"[RAG System] Đang xử lý tài liệu PDF: {self.pdf_path}...")
        if PdfReader is None:
            print("[RAG Warning] Package 'pypdf' không được cài; bỏ qua xử lý PDF.")
            return

        if self.client is None:
            print("[RAG Warning] Embedding client không khả dụng; bỏ qua xử lý PDF.")
            return

        reader = PdfReader(self.pdf_path)
        raw_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                raw_text += extracted + "\n"

        chunks = [raw_text[i:i+500] for i in range(0, len(raw_text), 400)]
        documents, embeddings, ids = [], [], []

        for idx, chunk in enumerate(chunks):
            if chunk.strip():
                documents.append(chunk)
                
                # Tạo embedding bằng genai SDK mới
                response = self.client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=chunk,
                )
                embeddings.append(response.embeddings[0].values)
                ids.append(f"chunk_{idx}")

        if documents:
            self.collection.add(documents=documents, embeddings=embeddings, ids=ids)
            print(f"[RAG System] Đã nạp thành công {len(documents)} đoạn tri thức vào ChromaDB.")

    def query_context(self, query: str, top_k: int = 3) -> str:
        if self.collection.count() == 0:
            return ""

        if self.client is None:
            print("[RAG Warning] Embedding client không khả dụng; trả về rỗng.")
            return ""

        query_emb = self.client.models.embed_content(
            model="gemini-embedding-2",
            contents=query,
        ).embeddings[0].values

        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )
        return "\n---\n".join(results.get('documents', [[]])[0])