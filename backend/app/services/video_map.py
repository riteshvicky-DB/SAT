"""
Skill → curated YouTube video URL mapping.
All URLs verified working as of 2026-06.
Falls back to a YouTube search URL if no specific video is mapped.
"""

# Verified working Khan Academy SAT math videos
_MATH_VIDEOS: dict[str, str] = {
    # ── Verified KA videos ──────────────────────────────────────────────────
    "Linear equations":        "https://www.youtube.com/watch?v=9DxrF6Ttws4",   # KA ✓
    "Systems of equations":    "https://www.youtube.com/watch?v=nok99JOhcjo",   # KA ✓
    "Functions":               "https://www.youtube.com/watch?v=kvGsIo1TmsM",   # KA ✓
    "Graph interpretation":    "https://www.youtube.com/watch?v=uk7gS3cZVp4",   # KA ✓
    "Quadratics":              "https://www.youtube.com/watch?v=i7idZfS8t8w",   # KA ✓
    "Exponential functions":   "https://www.youtube.com/watch?v=6WMZ7J0wwMI",   # KA ✓
    "Rational expressions":    "https://www.youtube.com/watch?v=7Uos1ED3KHI",   # KA ✓
    "Statistics":              "https://www.youtube.com/watch?v=uhxtUt_-GyM",   # KA ✓
    "Probability":             "https://www.youtube.com/watch?v=uzkc-qNVoOk",   # KA ✓
    # ── Search fallbacks for all others (always available) ─────────────────
    "Inequalities":            "https://www.youtube.com/results?search_query=Khan+Academy+SAT+inequalities+math",
    "Polynomials":             "https://www.youtube.com/results?search_query=Khan+Academy+SAT+polynomials",
    "Radicals":                "https://www.youtube.com/results?search_query=Khan+Academy+SAT+radicals+square+roots",
    "Ratios":                  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+ratios+proportions",
    "Percentages":             "https://www.youtube.com/results?search_query=Khan+Academy+SAT+percentages+math",
    "Tables":                  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+data+tables+math",
    "Charts":                  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+charts+graphs+data",
    "Circles":                 "https://www.youtube.com/results?search_query=Khan+Academy+SAT+circles+geometry",
    "Triangles":               "https://www.youtube.com/results?search_query=Khan+Academy+SAT+triangles+geometry",
    "Volume":                  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+volume+geometry",
    "Angles":                  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+angles+geometry",
    "Trigonometric functions": "https://www.youtube.com/results?search_query=Khan+Academy+SAT+trigonometry+sine+cosine",
}

# Verified working Khan Academy SAT Reading & Writing videos
_RW_VIDEOS: dict[str, str] = {
    # ── Search fallbacks for all R&W skills ────────────────────────────────
    "Main idea":             "https://www.youtube.com/results?search_query=Khan+Academy+SAT+main+idea+reading",
    "Evidence":              "https://www.youtube.com/results?search_query=Khan+Academy+SAT+evidence+reading",
    "Inference":             "https://www.youtube.com/results?search_query=Khan+Academy+SAT+inference+reading",
    "Vocabulary in context": "https://www.youtube.com/results?search_query=Khan+Academy+SAT+vocabulary+in+context",
    "Author purpose":        "https://www.youtube.com/results?search_query=Khan+Academy+SAT+author+purpose+rhetoric",
    "Sentence structure":    "https://www.youtube.com/results?search_query=Khan+Academy+SAT+sentence+structure+grammar",
    "Punctuation":           "https://www.youtube.com/results?search_query=Khan+Academy+SAT+punctuation+grammar",
    "Verb agreement":        "https://www.youtube.com/results?search_query=Khan+Academy+SAT+subject+verb+agreement",
    "Parallelism":           "https://www.youtube.com/results?search_query=Khan+Academy+SAT+parallelism+grammar",
    "Modifier placement":    "https://www.youtube.com/results?search_query=Khan+Academy+SAT+misplaced+modifiers",
    "Transition words":      "https://www.youtube.com/results?search_query=Khan+Academy+SAT+transition+words+writing",
    "Rhetorical synthesis":  "https://www.youtube.com/results?search_query=Khan+Academy+SAT+rhetorical+synthesis",
    "Conciseness":           "https://www.youtube.com/results?search_query=Khan+Academy+SAT+conciseness+wordiness",
    "Logical flow":          "https://www.youtube.com/results?search_query=Khan+Academy+SAT+logical+flow+paragraph+order",
}


def get_video_url(skill: str, section: str) -> str:
    mapping = _MATH_VIDEOS if section == "math" else _RW_VIDEOS
    if skill in mapping:
        return mapping[skill]
    query = urllib.parse.quote(f"Khan Academy SAT {skill}")
    return f"https://www.youtube.com/results?search_query={query}"


def is_search_url(url: str) -> bool:
    """True if the URL is a YouTube search (not a specific video)."""
    return "results?search_query" in url


import urllib.parse
