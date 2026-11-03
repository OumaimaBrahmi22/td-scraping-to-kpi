
import csv
import json
import requests
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:8b"

INPUT_FILE = Path("data/jobs_sample.csv")
OUTPUT_FILE = Path("data/extracted.json")

N_POSTINGS = int(sys.argv[1]) if len(sys.argv) > 1 else 15
MAX_CHARS = 1500


def extract_skills(description):
    prompt = f"""
Extract concrete technical skills, tools, programming languages,
frameworks and technologies from this job description.

Return only a JSON object with this structure:
{{"required_skills": ["Python", "AWS", "SQL"]}}

Do not include generic soft skills.
If no technical skills are found, return an empty list.

Job description:
{description[:MAX_CHARS]}
"""

    for attempt in range(3):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "think": False
                },
                timeout=(10, 120)
            )
            response.raise_for_status()

            result = response.json()
            extracted = json.loads(result["response"])

            return extracted.get("required_skills", [])

        except Exception as error:
            print(f"Attempt {attempt + 1} failed: {error}")
            if attempt == 2:
                return []
            time.sleep(5)


def main():
    with open(INPUT_FILE, encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    results = []

    for index, row in enumerate(
        [r for r in rows if r.get("description")][:N_POSTINGS],
        start=1
    ):
        skills = extract_skills(row["description"])

        results.append({
            "title": row.get("title", ""),
            "company": row.get("company", ""),
            "required_skills": skills
        })

        print(f"[{index}] {row.get('title', '')}: {skills}")

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "postings": results
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Saved {len(results)} postings to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

