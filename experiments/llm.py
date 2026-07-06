def generate_commentary(experiment, past_experiments):
    """
    Returns LLM-generated commentary on an experiment's results, or "" if no
    provider is configured.

    No LLM provider is wired in yet (see
    docs/superpowers/specs/2026-07-06-experiments-app-design.md) — this
    function is the extension point for that work. `experiment` and
    `past_experiments` are accepted now so callers (the training task) don't
    need to change when a provider is added later.
    """
    return ""
