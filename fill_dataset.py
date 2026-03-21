
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
import time
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")

# Load dataset
df = pd.read_excel("ua_resources.xlsx")

# ✅ Ensure column exists FIRST
if "student_queries" not in df.columns:
    df["student_queries"] = ""


# ------------------ FUNCTIONS ------------------

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    words = text.split()
    cleaned = [words[0]] if words else []

    for w in words[1:]:
        if w != cleaned[-1]:
            cleaned.append(w)

    return " ".join(cleaned)


def generate_fields(name, category, subcategory):
    prompt = f"""
You are building a HIGH-PRECISION semantic search dataset for university services.

STRICT RULES:
- ONLY describe what THIS service actually does
- DO NOT include unrelated actions
- Be precise and factual

Given:
Name: {name}
Category: {category}
Subcategory: {subcategory}

Generate:

description: One sentence starting with "Used to..."
target_users: comma-separated
keywords: real search phrases
student_queries: 5–8 realistic student questions

Return EXACTLY:

description: ...
target_users: ...
keywords: ...
student_queries: ...
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    text = response.choices[0].message.content

    try:
        desc = text.split("description:")[1].split("target_users:")[0].strip()
        users = text.split("target_users:")[1].split("keywords:")[0].strip()
        keywords = text.split("keywords:")[1].split("student_queries:")[0].strip()
        queries = text.split("student_queries:")[1].strip()
    except:
        desc, users, keywords, queries = "", "", "", ""

    return desc, users, keywords, queries


def validate_row(name, description, keywords, queries):
    prompt = f"""
Validate this dataset row.

Reject if:
- generic
- incorrect
- mismatched queries

Name: {name}
Description: {description}
Keywords: {keywords}
Queries: {queries}

Return ONLY:
valid
or
invalid
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.lower().strip()
    return result == "valid"


# ------------------ GENERATION LOOP ------------------

for i in tqdm(range(len(df))):
    if pd.isna(df.loc[i, "description"]) or df.loc[i, "description"] == "":
        name = df.loc[i, "resource_name"]
        category = df.loc[i, "category"]
        subcategory = df.loc[i, "subcategory"]

        for attempt in range(3):
            desc, users, keywords, queries = generate_fields(name, category, subcategory)

            if validate_row(name, desc, keywords, queries):
                break

        df.loc[i, "description"] = desc
        df.loc[i, "target_users"] = users
        df.loc[i, "keywords"] = keywords
        df.loc[i, "student_queries"] = queries

        time.sleep(0.3)


# ------------------ CLEAN AFTER GENERATION ------------------

df["student_queries"] = df["student_queries"].apply(clean_text)
df["keywords"] = df["keywords"].apply(clean_text)


# ------------------ BUILD SEARCH TEXT ------------------

print("Building optimized search_text...")

df["search_text"] = (
    (df["resource_name"].fillna("") + " ") * 3 +
    (df["student_queries"].fillna("") + " ") * 2 +
    df["description"].fillna("") + " " +
    df["keywords"].fillna("") + " " +
    df["category"].fillna("") + " " +
    df["subcategory"].fillna("")
).str.lower()


# Save
df.to_excel("ua_resources_filled.xlsx", index=False)

print("DONE 🚀")
