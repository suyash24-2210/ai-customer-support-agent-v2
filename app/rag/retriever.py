"""
Semantic retrieval for the customer support knowledge base.
"""

from sentence_transformers import SentenceTransformer, util

from app.rag.knowledge import SUPPORT_ARTICLES


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


article_texts = [
    f"{article['title']}. {article['content']}"
    for article in SUPPORT_ARTICLES
]


article_embeddings = embedding_model.encode(
    article_texts,
    convert_to_tensor=True,
    normalize_embeddings=True,
)


def retrieve_articles(
    query: str,
    category: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    """
    Return the most semantically relevant support articles.

    A small category bonus is applied when the article category
    matches the category predicted by the ticket classifier.
    """

    query_embedding = embedding_model.encode(
        query,
        convert_to_tensor=True,
        normalize_embeddings=True,
    )

    scores = util.cos_sim(
        query_embedding,
        article_embeddings,
    )[0]

    adjusted_scores = scores.clone()

    if category:
        for index, article in enumerate(SUPPORT_ARTICLES):
            if article["category"] == category:
                adjusted_scores[index] += 0.08

    top_indices = adjusted_scores.argsort(
        descending=True
    )[:top_k]

    results = []

    for index in top_indices.tolist():
        article = SUPPORT_ARTICLES[index].copy()

        article["similarity_score"] = round(
            float(scores[index]),
            4,
        )

        results.append(article)

    return results