# sources/user-network-fs/impacket/tox.ini

Purpose: Defines Impacket's tox test matrix, pytest/coverage commands, GitHub Actions Python mapping, and coverage reporting configuration.

Important APIs, types, and functions: Configures `[tox] envlist` for `clean`, Python 3.6-3.11, and `report`; `[gh-actions]` version mapping; `[testenv]` dependencies, `REMOTE_CONFIG` pass-through, `pip check`, and `pytest --cov`; coverage clean/report/html environments; pytest marker `remote`; and coverage omit/exclude rules.

Control flow: Tox runs `clean` before Python test environments, appends coverage per environment, then runs `report`. `py311` is allowed to ignore errors.

State and persistence behavior: Creates coverage data and HTML reports during tox runs. Passes `REMOTE_CONFIG` from the host environment for remote tests.

Dependencies and integration points: Integrates tox, pytest, coverage, requirements-test.txt, and GitHub Actions matrix selection.

Risks: `py311 ignore_errors = true` can hide failures on that interpreter. Coverage paths omit `remcom` and `.tox`; broad exclusions can mask untested defensive paths.

Test signals: Defines the primary local/CI test contract, multi-version compatibility coverage, remote marker metadata, and coverage reporting behavior.
