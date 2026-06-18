# sources/sync-backup/bup/wvtest.sh

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/wvtest.sh -->
## sources/sync-backup/bup/wvtest.sh

Purpose: this is Bup's shell assertion harness. It exposes WvTest-style helpers for POSIX shell tests, with richer diagnostics when sourced from Bash. It also normalizes Bup test environment defaults by setting `BUP_TEST_LEVEL`, `BUP_DIR`, and `GIT_DIR`.

Important APIs and functions: `_wvtextclean` formats assertion text while disabling glob expansion. `_wvcheck` emits the canonical `! file:line text ok|FAILED` line and exits on failure. `WVEXPRC` asserts a command's exit status matches a shell case pattern. `WVPASS` and `WVFAIL` assert command success/failure. `WVPASSEQ` and `WVPASSNE` compare two strings. `WVPASSRC` and `WVFAILRC` assert the previous command's return code. `WVSTART`, `WVSKIP`, and `WVDIE` announce test sections, skips, and fatal failures.

Control flow: on source, the script sets defaults and conditionally sources `wvtest-bash.sh` for Bash-only stack/caller support. Non-Bash shells get no-op backtrace helpers and an "unknown:0" caller. Each assertion records the command, locates the caller, runs the test expression or command, and calls `_wvcheck`. Failures exit immediately with the failing code.

State and persistence: all state is shell process state plus stderr output. It deliberately points `BUP_DIR` and `GIT_DIR` to `/dev/null` unless tests override them, preventing accidental use of ambient repositories.

Dependencies and integration points: integrates with `wvtest-bash.sh` when Bash is available. It relies on shell builtins, test `[ ]`, and stderr output consumed by Bup's test runner. Bup tests source this file directly or through `wvtest-bup.sh`.

Risks: functions use `local`, which is not strictly POSIX in every `/bin/sh`. Assertion text intentionally expands `$*` unquoted after disabling globbing, so whitespace/newlines are normalized for output but still require care. `WVEXPRC` temporarily disables `set -e`, which is necessary but can surprise test authors.

Test signals: passing assertions emit `ok`; failures emit `FAILED`, optionally a Bash backtrace, and exit nonzero. `WVSKIP` emits `skip ok`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/wvtest.sh -->
