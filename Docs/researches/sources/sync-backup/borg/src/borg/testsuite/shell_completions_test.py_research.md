# sources/sync-backup/borg/src/borg/testsuite/shell_completions_test.py

## Purpose
Validates that Borg's Fish shell completion file is present and syntactically sourceable by Fish. It is a smoke test for generated/distributed shell completion assets.

## Important APIs, Types, and Functions
Uses `SHELL_COMPLETIONS_DIR`, `Path`, `subprocess.run`, and `pytest.skip`. The sole test is `test_fish_completion_is_valid`.

## Control Flow
The test computes the repository-relative completion path, asserts `scripts/shell_completions/fish/borg.fish` exists, probes `fish --version`, skips if Fish is unavailable, then sources the completion file with `fish -c`.

## State and Persistence Behavior
No persistent state is modified. The test reads a checked-in completion file and depends on the host system having Fish installed for full validation.

## Dependencies and Integration Points
Integrates the test suite with shell completion packaging. It catches syntax regressions that normal Python tests would miss.

## Risks and Test Signals
Risks are environment-dependent skips and shell-specific quoting errors. The key signal is zero exit status when sourcing the Fish completion file, with stderr reported on failure.
