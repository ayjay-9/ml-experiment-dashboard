from experiments.llm import generate_commentary


def test_generate_commentary_returns_empty_string_without_provider():
    assert generate_commentary(experiment=None, past_experiments=[]) == ""
