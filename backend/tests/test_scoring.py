from app.services.scoring import _probability, _section_score


def test_section_score_bounds() -> None:
    assert _section_score({"weighted": 0, "possible": 10}) == 200
    assert _section_score({"weighted": 10, "possible": 10}) == 800


def test_probability_increases_with_score() -> None:
    assert _probability(1500, 1500) > _probability(1400, 1500)
