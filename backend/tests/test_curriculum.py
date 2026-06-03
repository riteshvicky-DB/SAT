from app.services.curriculum import all_skills, slug_for_skill


def test_curriculum_contains_required_domains() -> None:
    skills = all_skills()
    names = {item["skill"] for item in skills}
    assert "Linear equations" in names
    assert "Inference" in names
    assert "Trigonometric functions" in names


def test_slug_for_skill() -> None:
    assert slug_for_skill("Algebra", "Linear equations") == "algebra-linear-equations"
