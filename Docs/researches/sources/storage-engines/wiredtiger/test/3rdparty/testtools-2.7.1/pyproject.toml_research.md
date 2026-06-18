# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/pyproject.toml

Purpose: modern build, packaging, metadata, extras, and mypy configuration for testtools 2.7.1.

Important APIs, types, and functions: `[tool.mypy]` enables redundant-cast, unused-config, and untyped-def checks, with missing imports ignored for optional packages. `[build-system]` uses `hatchling.build` with setuptools, hatchling, and hatch_vcs requirements. `[project]` declares package metadata, Python `>=3.7`, dynamic version, classifiers, and a conditional setuptools dependency for Python 3.12+. Optional dependencies define `test` and `twisted` extras. Hatch VCS configuration writes `testtools/_version.py` using a tag pattern.

Control flow: PEP 517 frontends install build requirements, invoke hatchling, derive version from VCS tags, and include the `testtools` package. Mypy reads tool settings when static analysis is run.

State and persistence: builds persist wheels/sdists and generated `_version.py` in build artifacts. No runtime state is stored by this file.

Dependencies and integration points: integrates with setuptools compatibility, hatchling, hatch_vcs, package extras used by CI, and the minimal `setup.py` shim.

Risks and test signals: `[tool.files]` and `[tool.extras]` are nonstandard for current PEP 621 consumers, while `[project.optional-dependencies]` is authoritative. VCS-derived versioning needs full Git metadata, reflected by CI checkout `fetch-depth: 0`. Test signals are successful `python -m build`, package install with extras, and mypy configuration loading.
