# File Research: sources/virtualization/nvme-cli/tests/tap_runner.py

TAP version 13 runner for Python unittest modules.

Key elements:
- Imports a named test module, loads tests with `unittest.TestLoader`, and emits TAP header and plan.
- `TAPDiagnosticStream` prefixes test stdout lines with `# ` so regular output remains TAP-compliant diagnostics.
- `TAPTestResult` emits `ok`, `not ok`, `# SKIP`, and TODO-style expected/unexpected failure lines.
- Failures/errors include YAML-ish traceback diagnostics on stderr.
- CLI supports `--start-dir` to prepend tests directory to `sys.path`.

Notable behavior:
- `main` always exits `0` after running tests, regardless of `result.wasSuccessful()`. Meson TAP parsing may still detect `not ok`, but process status alone will not indicate failure.
