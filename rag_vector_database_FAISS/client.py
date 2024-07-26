from sentence_transformers import SentenceTransformer
from vector_database import vector_database




documents = [
    "'To Kill a Mockingbird' is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature.",
    "The novel 'Moby-Dick' was written by Herman Melville and first published in 1851. It is considered a masterpiece of American literature and deals with complex themes of obsession, revenge, and the conflict between good and evil.",
    "Harper Lee, an American novelist widely known for her novel 'To Kill a Mockingbird', was born in 1926 in Monroeville, Alabama. She received the Pulitzer Prize for Fiction in 1961.",
    "Jane Austen was an English novelist known primarily for her six major novels, which interpret, critique and comment upon the British landed gentry at the end of the 18th century.",
    "The 'Harry Potter' series, which consists of seven fantasy novels written by British author J.K. Rowling, is among the most popular and critically acclaimed books of the modern era.",
    "'The Great Gatsby', a novel written by American author F. Scott Fitzgerald, was published in 1925. The story is set in the Jazz Age and follows the life of millionaire Jay Gatsby and his pursuit of Daisy Buchanan.",
    "Tiny changes rule in Atomic Habits. Focus on systems that make good habits easy and tempting, while hiding bad ones. These small wins compound over time, shaping who you are. Become the person you want to be by aligning your habits with your ideal identity"
    "Don't just resist bad habits, make good ones so appealing you crave them. When you exercise, tie it to a post-workout treat you genuinely enjoy.",
    "Goals are fleeting, but good systems create lasting change. Design your environment for success. Put your gym clothes next to your bed for a morning workout",
    "Your confidence in personal growth is key. See yourself as capable of change. If you believe you can build a good habit, you're halfway there." 
    "Don't get discouraged by setbacks. Celebrate small wins and focus on the journey of habit formation. Every step forward brings you closer to your goals."
]


# Use the sentence-transformers model for embeddings
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(model_name)

embedding_list = embedding_model.encode(documents)

my_db = vector_database()

my_db.insert_embeddings(embedding_list = embedding_list, chunk_list=documents, metadata={"source": "Atomic_Habits.pdf", "category": "Novel"})
