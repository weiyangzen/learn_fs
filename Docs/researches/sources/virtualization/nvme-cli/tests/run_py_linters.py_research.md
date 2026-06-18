# File Research: sources/virtualization/nvme-cli/tests/run_py_linters.py

Helper script for Meson Python lint and format targets.

Key elements:
- Reads `MESON_SOURCE_ROOT` and `MESON_BUILD_ROOT`.
- Targets the `tests` directory.
- `lint` mode runs `flake8` and strict `mypy` with Python 3.8, namespace packages, ignored missing imports, and a build-dir mypy cache.
- `format` mode gathers Python files and runs `autopep8 --in-place` followed by `isort` with vertical hanging indent and trailing commas.
- Does not fail fast because subprocess calls use `check=False`.

Role:
- Provides optional developer tooling targets rather than mandatory test enforcement.
