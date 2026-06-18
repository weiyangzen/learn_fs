# sources/security-integrity/cryfs/tools/detect-flaky-tests.py

Purpose: standalone Python/uv tool for detecting flaky Rust tests by building once and then running `cargo test` repeatedly with logs, adaptive timeouts, and optional Rich TUI display.

Important APIs/types/functions: `parse_args`, `repo_root`, `run_cargo`, `run_all`, `_setup_log_dir`, `Display`, `PlainDisplay`, `TuiDisplay`, `ReaderState`, `LogBuffer`, and `StatusState`. Constants define first-run timeout, subsequent timeout formula, log directory, refresh rate, reader polling, and process kill grace periods.

Control flow: `main()` validates POSIX, parses `--plain` and run count, creates `.flaky-runs/<timestamp>/`, forces `RUST_BACKTRACE=1` unless already more verbose, selects TUI/PTY only for interactive stdout, then calls `run_all()`. `run_all()` executes `cargo test --no-run` once, then loops N `cargo test` invocations. `run_cargo()` starts cargo in a new session, streams stdout/stderr to a reader thread, logs output, and kills the entire process group on timeout or interrupt.

State/persistence: persists `build.log`, `run-N.log`, and a best-effort `.flaky-runs/latest` symlink. In-memory status tracks elapsed durations for adaptive timeouts and display.

Dependencies/integration: Python 3.9+, uv PEP 723 metadata, Rich, POSIX process groups, PTYs, `cargo`, and CryFS repo root detection by `Cargo.toml`.

Risks: POSIX-only; PTY/log reader behavior is carefully handled but still may warn if descendants inherit pipes. It kills process groups, so forwarded cargo commands must not intentionally share unrelated processes in the same session. Logs can include test output secrets.

Test signals: the tool is itself a test harness; failures are build failure, first failing repeated run, timeout, reader error, or all-runs-success summary.
