<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml -->
# sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml

Purpose: Poetry project metadata and build configuration for vendored `iso8601` 2.1.0.

Important APIs/functions: `[tool.poetry]` declares package name, version, description, author, MIT license, README, homepage, repository, and documentation. Runtime dependency is `python >=3.7,<4.0`. Dev dependency group includes mypy, black, pytest, hypothesis, pytz, pre-commit, nox, Sphinx, changelog-manager, and ruff. `[build-system]` uses `poetry-core>=1.0.0`. `[tool.isort]` sets `profile = "black"`.

Control flow: Build and dependency tools consume the TOML; no runtime execution.

State and persistence behavior: Defines package metadata, build backend, and development dependency resolution. It does not affect parser behavior unless packaging/build commands are run.

Dependencies and integration points: Integrates with Poetry, PEP 517 build frontends, isort, and the pytest/Hypothesis test suite. WiredTiger vendors this metadata to preserve upstream package context.

Risks: Vendored environments that do not use Poetry may ignore dev dependency declarations. Version constraints allow Python 3.7 through 3.x but not Python 4. Tool dependencies are unpinned wildcards, which can make upstream development checks non-reproducible.

Test signals: Build smoke test is a PEP 517/Poetry build with poetry-core. Test/development environments should install pytest, hypothesis, and pytz to run `iso8601/test_iso8601.py`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/iso8601-2.1.0/pyproject.toml -->
