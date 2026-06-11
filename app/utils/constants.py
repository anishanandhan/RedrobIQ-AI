from datetime import datetime

# Deduplicated: each canonical concept listed once.
# Matching is substring-based so "embedding" catches "embeddings" etc.
MUST_HAVE_SKILLS = [
    "embedding", "sentence-transformer", "bge", "faiss", "qdrant", "pinecone", 
    "weaviate", "milvus", "opensearch", "elasticsearch", "vector search", 
    "vector database", "hybrid search", "retrieval augmented", "rag", "rerank", 
    "learning to rank", "information retrieval", "ndcg", "mrr", "llm", 
    "large language model", "a/b test", "evaluation framework",
]

NICE_TO_HAVE_SKILLS = [
    "lora", "qlora", "peft", "fine-tun", "xgboost", "lightgbm", "recommendation", 
    "hr tech", "recruiting", "distributed system", "inference optim", "triton", 
    "onnx", "open source", "open-source", "nlp", "bert",
]

DISQUALIFIER_TITLES = [
    "marketing manager", "customer support", "operations manager",
    "accountant", "civil engineer", "mechanical engineer", "hr manager",
    "sales", "business development", "recruiter", "finance",
    "supply chain", "legal", "content writer",
]

CONSULTING_FIRMS = [
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "mphasis", "hexaware",
]

PREFERRED_LOCATIONS_INDIA = [
    "pune", "noida", "hyderabad", "mumbai", "delhi", "bengaluru",
    "bangalore", "gurgaon", "gurugram", "ncr", "chennai", "kolkata",
    "ahmedabad", "kochi",
]

PRODUCT_COMPANY_SIGNALS = [
    "startup", "series a", "series b", "series c", "saas",
    "platform", "product",
]

JD_TARGET_CITIES = [
    "pune", "noida", "hyderabad", "bengaluru", "bangalore", "delhi", 
    "gurgaon", "gurugram", "ncr",
]

TODAY = datetime(2026, 6, 11)

# Pre-computed weights mapping the first 50 characters of unique job description templates to their fit scores
CAREER_TEMPLATE_WEIGHTS = {
    'Fine-tuned LLaMA-2-7B and Mistral-7B variants usin': 1.0,
    'Built a RAG-based ranking pipeline serving 50M+ qu': 1.0,
    'Built and shipped a production recommendation syst': 1.0,
    'Owned the end-to-end ranking pipeline at a recomme': 1.0,
    'Owned the design and rollout of a large-scale sema': 1.0,
    'Led the migration from keyword-based to embedding-': 1.0,
    'Built systems that understand what users are looki': 1.0,
    'Shipped the personalization infrastructure: the sy': 1.0,
    "Designed the ranking layer for the company's flags": 1.0,
    'Owned the search and discovery experience end-to-e': 1.0,
    'Led the engineering team building infrastructure t': 1.0,
    'Owned the ranking layer for an e-commerce search p': 0.9,
    'Trained and shipped multiple ranking models for ou': 0.9,
    'Developed a semantic search feature for an interna': 0.9,
    'Implemented a RAG-based customer support chatbot i': 0.8,
    'Built a content recommendation system serving 10M+': 0.8,
    'Built and operated production ML pipelines using M': 0.8,
    'Contributed to ML feature engineering and model de': 0.6,
    'Built recommendation-style features at a mid-stage': 0.6,
    "Built computer vision models for our product's ima": 0.6,
    'Worked on customer-facing predictive modeling for ': 0.6,
    'Built NLP pipelines for sentiment analysis and doc': 0.6,
    'Mixed data science and analytics-engineering role ': 0.3,
    'Worked on time-series forecasting models for suppl': 0.3,
    'Designed and maintained the analytical data wareho': 0.1,
    'Built and maintained data pipelines on Apache Airf': 0.1,
    'Backend + data hybrid role at a growth-stage start': 0.1,
    'Implemented streaming data pipelines on Kafka and ': 0.1,
    'Backend development with Python (FastAPI), Postgre': 0.1,
    'Enterprise sales of cloud software solutions into ': 0.0,
    'Customer support team lead at a SaaS product. Mana': 0.0,
    'Marketing leadership role at a B2B SaaS company. O': 0.0,
    'Business analyst at a consulting firm, working pri': 0.0,
    'Brand design and creative direction at a consumer-': 0.0,
    'Mechanical engineering design role at a hardware-p': 0.0,
    'Senior accounting role at a mid-sized company — mo': 0.0,
    'Content writing and SEO strategy for a tech-focuse': 0.0,
    'Operations management role at a logistics company.': 0.0,
    'Cloud infrastructure and DevOps work at an enterpr': 0.0,
    'Android mobile development using Java and (more re': 0.0,
    'Frontend engineering at a media company. React, Ty': 0.0,
    'Java backend development at a large enterprise — S': 0.0,
    'Full-stack web application development at a SaaS c': 0.0,
    'Test automation and QA engineering for a fintech p': 0.0,
}
