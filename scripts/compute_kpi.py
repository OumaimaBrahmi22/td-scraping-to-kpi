
import json
from collections import Counter
from pathlib import Path

INPUT_FILE = Path("data/extracted.json")
OUTPUT_FILE = Path("docs/data/kpi.json")

TARGET_SKILL = "python"


def main():
    # Load extracted data
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    postings = data["postings"]

    # Count all extracted skills
    skill_counts = Counter()

    for posting in postings:
        skills = posting.get("required_skills", [])
        skill_counts.update(skills)

    # Count postings mentioning the target skill
    matching_postings = sum(
        1 for posting in postings
        if any(
            TARGET_SKILL.lower() in skill.lower()
            for skill in posting.get("required_skills", [])
        )
    )

    total_postings = len(postings)

    # Calculate KPIs
    kpi = {
        "total_postings": total_postings,
        "target_skill": TARGET_SKILL,
        "postings_with_target_skill": matching_postings,
        "target_skill_fraction": (
            matching_postings / total_postings
            if total_postings else 0
        ),
        "average_skills_per_posting": (
            sum(
                len(posting.get("required_skills", []))
                for posting in postings
            ) / total_postings
            if total_postings else 0
        ),
        "top_10_skills": skill_counts.most_common(10)
    }

    # Save aggregated results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(kpi, file, indent=2, ensure_ascii=False)

    print(json.dumps(kpi, indent=2, ensure_ascii=False))
    print(f"\nKPI saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
