# sources/test-tools/syzkaller/executor/executor_common.h

Purpose: Tiny executor utility header currently providing command-line option extraction shared by executor code and tests.

Important API and control flow: `get_last_opt(cmdline, key, out, out_len)` constructs `key=`, scans all occurrences in the command line, accepts only matches at the beginning or after whitespace, remembers the last valid value, then copies it into `out` truncated to `out_len - 1`.

State and dependencies: stateless helper depending on `snprintf`, `strstr`, `strlen`, `strcspn`, and `memcpy`. It does not clear `out` when no match is found, so callers should initialize defaults first.

Integration points: Linux kdump setup in `executor_linux.h` uses it to preserve `root` and `console` options when constructing a crash-kernel command line. `test.h` includes focused tests for whitespace, multiple occurrences, non-matches, and truncation.

Risks and tests: `key_eq` is limited to 128 bytes, so extremely long keys are truncated. The parser is intentionally simple and does not handle quoting. `test_get_last_opt` is the direct regression signal.
