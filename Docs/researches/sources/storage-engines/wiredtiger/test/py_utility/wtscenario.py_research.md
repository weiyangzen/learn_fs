# sources/storage-engines/wiredtiger/test/py_utility/wtscenario.py

Purpose: scenario-generation utilities for WiredTiger Python tests, including cross products, probabilistic pruning, long-run filtering, numbering, and page-size scenario generation.

Important APIs and control flow: `powerrange()` yields multiplicative ranges including the stop value. `make_scenarios()` multiplies scenario lists, applies optional include/prune/prunelong rules, and numbers them. `multiply_scenarios()` creates cross products, merges dictionaries, multiplies `P` probabilities when both sides provide them, and suppresses `long_only` combinations unless long runs are enabled. `prune_scenarios()` either filters by probability or chooses a bounded count using `suite_random`. `number_scenarios()` mutates dictionaries with `scenario_name` and `scenario_number`. `wtscenario.session_create_scenario()` generates combinations of page size/cache settings and exposes `shortName()`/`configString()`.

State and persistence behavior: module-level `_is_long_run` gates long-only scenarios. Scenario dictionaries are mutated in place during numbering and temporary pruning metadata insertion/removal.

Dependencies and integration points: depends on `suite_random` and is consumed by many Python test classes through a `scenarios` class variable. Generated config strings feed `session.create`.

Risks: duplicate names assert at runtime. In-place dictionary mutation can surprise callers sharing scenario dictionaries. `log2chr()` uses `/`, producing floats in Python 3 during repeated division, though comparisons and integer-like values still produce character offsets only if coerced safely by `chr` inputs.

Test signals: runners should list unique, numbered scenario names and execute deterministic subsets under fixed seeds and long-run settings.
