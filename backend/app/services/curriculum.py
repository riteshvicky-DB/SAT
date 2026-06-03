SAT_CURRICULUM = {
    "math": {
        "Algebra": [
            "Linear equations",
            "Systems of equations",
            "Inequalities",
            "Functions",
            "Graph interpretation",
        ],
        "Advanced Math": [
            "Quadratics",
            "Polynomials",
            "Exponential functions",
            "Radicals",
            "Rational expressions",
        ],
        "Problem Solving and Data Analysis": [
            "Ratios",
            "Percentages",
            "Statistics",
            "Probability",
            "Tables",
            "Charts",
        ],
        "Geometry and Trigonometry": [
            "Circles",
            "Triangles",
            "Volume",
            "Angles",
            "Trigonometric functions",
        ],
    },
    "reading_writing": {
        "Reading": [
            "Main idea",
            "Evidence",
            "Inference",
            "Vocabulary in context",
            "Author purpose",
        ],
        "Grammar": [
            "Sentence structure",
            "Punctuation",
            "Verb agreement",
            "Parallelism",
            "Modifier placement",
        ],
        "Writing": [
            "Transition words",
            "Rhetorical synthesis",
            "Conciseness",
            "Logical flow",
        ],
    },
}


def slug_for_skill(domain: str, skill: str) -> str:
    raw = f"{domain}-{skill}".lower()
    return raw.replace("&", "and").replace(" ", "-").replace("/", "-")


def all_skills() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for section, domains in SAT_CURRICULUM.items():
        for domain, skills in domains.items():
            for skill in skills:
                rows.append(
                    {
                        "section": section,
                        "domain": domain,
                        "skill": skill,
                        "slug": slug_for_skill(domain, skill),
                    }
                )
    return rows
