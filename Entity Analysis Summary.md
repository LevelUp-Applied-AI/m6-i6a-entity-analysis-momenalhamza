# Entity Analysis Summary

## Corpus Overview

The climate corpus contains 200 articles:

* 132 English articles
* 68 Arabic articles

The articles are distributed across four categories:

* Adaptation: 61 articles
* Science: 50 articles
* Impact: 46 articles
* Policy: 43 articles

A total of 1202 named entities were extracted using the spaCy NER pipeline.

---

# Entity Type Distribution

The most common entity types in the corpus are:

| Entity Type | Count |
| ----------- | ----- |
| DATE        | 256   |
| ORG         | 184   |
| GPE         | 165   |
| CARDINAL    | 138   |
| PERCENT     | 103   |

The dominance of DATE entities indicates that climate articles frequently reference future goals, timelines, annual reports, and policy deadlines. High counts of ORG and GPE entities suggest that climate discourse strongly focuses on organizations, governments, institutions, and geographic regions.

---

# Most Frequent Entities

The top entities extracted from the corpus are:

| Entity   | Type | Count |
| -------- | ---- | ----- |
| 2030     | DATE | 25    |
| 2023     | DATE | 21    |
| Jordan   | GPE  | 16    |
| annually | DATE | 15    |
| annual   | DATE | 10    |

The prominence of “2030” reflects the importance of long-term sustainability goals and climate action plans. “Jordan” appears frequently, showing regional relevance in the dataset.

---

# Category-Level Patterns

Different article categories emphasize different entity types:

* Science articles contain the highest number of DATE entities, reflecting research timelines, reports, and climate projections.
* Policy articles also heavily rely on DATE entities because climate agreements and government plans are often tied to deadlines and target years.
* Adaptation articles contain many GPE entities, indicating a focus on geographic regions and local climate impacts.
* ORG entities are especially common in science and policy articles, highlighting the role of institutions and international organizations in climate discussions.

These patterns demonstrate that entity distribution changes depending on the topic and purpose of the article category.

---

# Co-occurrence Insights

The most frequent co-occurring entity pairs are:

| Entity Pair       | Co-occurrence Count |
| ----------------- | ------------------- |
| Jordan ↔ annually | 7                   |
| 2030 ↔ Jordan     | 5                   |
| 2023 ↔ 2030       | 5                   |

These relationships suggest that climate discussions in the corpus are strongly connected to long-term national planning, yearly reporting, and sustainability targets.

---

# Overall Interpretation

The entity analysis reveals that climate discourse is primarily driven by:

* timelines and future targets,
* governments and organizations,
* geographically specific climate issues.

The combination of DATE, ORG, and GPE entities indicates that the corpus focuses heavily on international cooperation, policy development, climate planning, and regional environmental impacts.
