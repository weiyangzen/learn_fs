# sources/sync-backup/bup/test/int/test_helpers.py

Purpose: integration-style unit coverage for `bup.helpers` path, parsing, process-cleanup, atomic-write, timezone, shell-string, and save-name helpers. It verifies both pure utility behavior and filesystem/process side effects that bup commands depend on.

Important APIs/types/functions: imports `parse_num`, `detect_fakeroot`, `path_components`, `stripped_path_components`, `grafted_path_components`, `shstr`, `finalized`, `stopped`, `partition`, `atomically_replaced_file`, `utc_offset_str`, and `helpers.valid_save_name`. It also defines `set_tz()` to mutate `bup.compat.environ[b'TZ']` and call `tzset()`.

Control flow: tests are independent pytest functions. Numeric parsing covers bytes/str, decimal and exponential units, and negative values. Path tests validate absolute-only behavior, strip roots, and graft mapping. `test_stopped()` launches `true`, ordinary `sleep`, and a SIGTERM-ignoring child, then exercises normal exit, exception exit, SIGTERM, and SIGKILL escalation. Atomic replacement writes a target, verifies rollback on exception, and checks text/binary modes with both sync settings.

State and persistence behavior: mutates subprocess state, local temporary files, and process environment. `test_utc_offset_str()` restores the original `TZ`; `atomically_replaced_file()` must leave the previous target content intact on failure. The process tests assert real signal-derived return codes.

Dependencies/integration points: uses `Popen`, POSIX signals, `tzset`, pytest parametrization, `wvpytest` aliases, `bup.compat.environ`, and helper internals. It validates helpers used by bup command-line execution, archive path construction, cleanup contexts, and Git save-name safety.

Risks and test signals: signal tests are timing/platform sensitive and assume `sleep` is available. Timezone tests depend on libc TZ parsing. The strongest signals are exact result lists for path helpers, expected process termination codes, preserved file contents after failed atomic replacement, and rejection of Git-unsafe save names.
