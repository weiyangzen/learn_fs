# File Research: sources/virtualization/nvme-cli/tests/meson.build

Meson definition for Python integration tests and Python lint/format targets.

Key elements:
- Lists test infrastructure files and concrete test modules.
- Runs each test module through `tap_runner.py --start-dir <tests_dir> <module>`.
- Sets `PATH` so the project build root precedes system binary paths.
- Uses TAP protocol, serial execution, and 500-second timeout.
- Adds optional `lint-python` target when `mypy` and `flake8` are found.
- Adds optional `format-python` target when `autopep8` and `isort` are found.

Role:
- Integrates hardware-backed Python tests into Meson while producing TAP output.
