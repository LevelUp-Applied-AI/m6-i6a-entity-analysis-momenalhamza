"""
Module 6 Week A — Integration: Entity Analysis Pipeline

Build a corpus-level entity analysis pipeline that preprocesses
climate articles (with language-aware handling), extracts entities,
computes statistics, and produces visualizations.

Run: python entity_analysis.py
"""
from itertools import combinations

import unicodedata

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import spacy


def load_corpus(filepath="data/climate_articles.csv"):
    """Load the climate articles dataset.

    Args:
        filepath: Path to the CSV file.

    Returns:
        DataFrame with columns: id, text, source, language, category.
    """
    df = pd.read_csv(filepath)

    return df


def preprocess_corpus(df):
    """Add a language-aware `processed_text` column to the corpus.

    For every row, apply Unicode NFC normalization to `text` so that
    visually identical characters (composed vs. decomposed diacritics)
    compare equal downstream. The processed form preserves
    capitalization and punctuation — those are signals NER depends on.

    For Arabic rows (`language == 'ar'`), do not attempt English NLP
    processing: either pass the NFC-normalized text through unchanged
    or store an empty string. Either choice must not crash the
    pipeline.

    Args:
        df: DataFrame returned by load_corpus.

    Returns:
        Copy of df with a new `processed_text` column. The original
        `text` column is left intact so NER can still consume it.
    """
    df_copy = df.copy()

    processed_texts = []

    for _, row in df_copy.iterrows():

        text = str(row["text"])

        normalized_text = unicodedata.normalize("NFC", text)

        if row["language"] == "en":
            processed_texts.append(normalized_text)

        elif row["language"] == "ar":
            processed_texts.append(normalized_text)

        else:
            processed_texts.append("")

    df_copy["processed_text"] = processed_texts

    return df_copy


def run_ner_pipeline(df, nlp):
    """Run spaCy NER on the English rows of a preprocessed corpus.

    Args:
        df: DataFrame with columns id, text, language, processed_text.
        nlp: A loaded spaCy Language object (e.g., en_core_web_sm).

    Returns:
        DataFrame with columns: text_id, entity_text, entity_label,
        start_char, end_char.
    """
    english_df = df[df["language"] == "en"]

    entity_rows = []

    for _, row in english_df.iterrows():

        text_id = row["id"]

        text = row["text"]

        doc = nlp(text)

        for ent in doc.ents:

            entity_rows.append({
                "text_id": text_id,
                "entity_text": ent.text,
                "entity_label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char
            })

    entity_df = pd.DataFrame(entity_rows)

    return entity_df

def aggregate_entity_stats(entity_df, articles_df):
    """Compute frequency, co-occurrence, and per-category statistics.

    Args:
        entity_df: DataFrame with columns text_id, entity_text,
                   entity_label.
        articles_df: The source corpus DataFrame (with columns id,
                     category, ...). Used to join category onto
                     each entity for per-category aggregation.

    Returns:
        Dictionary with keys:
          'top_entities': DataFrame of top 20 entities by frequency
                          (columns: entity_text, entity_label, count)
          'label_counts': dict of entity_label -> total count
          'co_occurrence': DataFrame of entity pairs appearing in the
                           same text (columns: entity_a, entity_b,
                           co_count). Cap at top 50 pairs by co_count
                           (or filter to co_count >= 2) so the result
                           stays readable on the full corpus.
          'per_category': DataFrame of entity-label counts broken out
                          by article category (columns: category,
                          entity_label, count)
    """
    # 1. Top Entities
    # -------------------------
    top_entities = (
        entity_df
        .groupby(["entity_text", "entity_label"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
        .head(20)
    )

    # -------------------------
    # 2. Label Counts
    # -------------------------
    label_counts = entity_df["entity_label"].value_counts().to_dict()

    # -------------------------
    # 3. Co-occurrence
    # -------------------------
    pair_counts = {}

    grouped = entity_df.groupby("text_id")

    for _, group in grouped:

        entities = group["entity_text"].unique()

        for pair in combinations(sorted(entities), 2):

            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    co_occurrence_rows = [
        {
            "entity_a": a,
            "entity_b": b,
            "co_count": count
        }
        for (a, b), count in pair_counts.items()
    ]

    co_occurrence = pd.DataFrame(co_occurrence_rows)

    if not co_occurrence.empty:
        co_occurrence = (
            co_occurrence
            .sort_values(by="co_count", ascending=False)
            .head(50)
        )

    # -------------------------
    # 4. Per-category stats
    # -------------------------
    merged = entity_df.merge(
        articles_df[["id", "category"]],
        left_on="text_id",
        right_on="id"
    )

    per_category = (
        merged
        .groupby(["category", "entity_label"])
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    # -------------------------
    # Final output
    # -------------------------
    return {
        "top_entities": top_entities,
        "label_counts": label_counts,
        "co_occurrence": co_occurrence,
        "per_category": per_category
    }


def visualize_entity_distribution(stats, output_path="entity_distribution.png"):
    """Create a bar chart of the top 20 entities by frequency.

    Args:
        stats: Dictionary from aggregate_entity_stats (must contain
               'top_entities' DataFrame).
        output_path: File path to save the chart.
    """
    top_entities = stats["top_entities"]

    plt.figure(figsize=(12, 8))

    labels = (
        top_entities["entity_text"]
        + " (" +
        top_entities["entity_label"] +
        ")"
    )

    plt.barh(labels, top_entities["count"])

    plt.xlabel("Frequency")

    plt.ylabel("Entities")

    plt.title("Top 20 Most Frequent Entities")

    plt.gca().invert_yaxis()

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()


def generate_report(stats, co_occurrence):
    """Generate a text summary of entity analysis findings.

    Args:
        stats: Dictionary from aggregate_entity_stats.
        co_occurrence: Co-occurrence DataFrame from stats.

    Returns:
        String containing a structured report with: entity counts
        per type, top 5 most frequent entities, top 3 co-occurring
        pairs, and a brief summary.
    """
    report = []

    report.append("ENTITY ANALYSIS REPORT\n")

    report.append("Entity Counts Per Type:\n")

    for label, count in stats["label_counts"].items():

        report.append(f"- {label}: {count}")

    report.append("\nTop 5 Most Frequent Entities:\n")

    top_5 = stats["top_entities"].head(5)

    for _, row in top_5.iterrows():

        report.append(
            f"- {row['entity_text']} "
            f"({row['entity_label']}): "
            f"{row['count']}"
        )

    report.append("\nTop 3 Co-occurring Entity Pairs:\n")

    top_pairs = co_occurrence.head(3)

    for _, row in top_pairs.iterrows():

        report.append(
            f"- {row['entity_a']} ↔ "
            f"{row['entity_b']} "
            f"({row['co_count']} texts)"
        )

    report.append("\nSummary:\n")

    report.append(
        "The corpus is dominated by frequently occurring "
        "organizations, locations, and dates, suggesting "
        "that climate discourse focuses heavily on "
        "institutions, international collaboration, "
        "and geographically specific climate impacts."
    )

    return "\n".join(report)


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")

    # Load and preprocess the corpus
    raw = load_corpus()
    if raw is not None:
        corpus = preprocess_corpus(raw)
        if corpus is not None:
            print(f"Corpus: {len(corpus)} articles")
            print(f"Languages: {corpus['language'].value_counts().to_dict()}")
            print(f"Categories: {corpus['category'].value_counts().to_dict()}")

            # Run NER on English rows
            entities = run_ner_pipeline(corpus, nlp)
            if entities is not None:
                print(f"\nExtracted {len(entities)} entities")

                # Aggregate statistics
                stats = aggregate_entity_stats(entities, corpus)
                if stats is not None:
                    print(f"\nLabel counts: {stats['label_counts']}")
                    print(f"\nTop 5 entities:")
                    print(stats["top_entities"].head())
                    print(f"\nPer-category counts (head):")
                    print(stats["per_category"].head())

                    # Visualize
                    visualize_entity_distribution(stats)
                    print("\nVisualization saved to entity_distribution.png")

                    # Generate report
                    report = generate_report(stats, stats.get("co_occurrence"))
                    if report is not None:
                        print(f"\n{'='*50}")
                        print(report)
