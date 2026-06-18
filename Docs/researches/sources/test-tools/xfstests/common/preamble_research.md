## sources/test-tools/xfstests/common/preamble

Purpose: this file is the standard setup entry point for modern fstests scripts. It initializes per-test globals, installs cleanup, sources the common runtime, and records basic QA output.

Important APIs: `_cleanup` is the default cleanup that kills fsstress if available, changes to `/`, and removes `$tmp.*`. `_register_cleanup cleanup [signals...]` installs a trap for EXIT, HUP, INT, QUIT, TERM, and optional extra signals, appending `exit $status`. `_begin_fstest group...` is the canonical bootstrap called near the top of tests.

Control flow: `_begin_fstest` sources `common/exit` and `common/test_names`, rejects double invocation when `$seq` is already set, derives `seq` from `$0`, sets `seqres`, prints the QA output banner, initializes `here`, `tmp`, and `status=1`, registers cleanup, sources `./common/rc`, calls `init_rc`, and removes previous `$seqres.full` and `$seqres.hints`.

State and persistence: it creates no durable data directly, but it defines the core per-test state consumed by the rest of fstests: `seq`, `seqres`, `here`, `tmp`, and default failing `status`. It also removes stale full logs/hints for the current sequence and installs process-global shell traps.

Dependencies and integration: every test in this subset sources it first and calls `_begin_fstest` with group tags such as `auto`, `quick`, `snapshot`, `send`, `raid`, and `qgroup`. It depends on `common/exit`, `common/test_names`, `common/rc`, `_kill_fsstress`, and `_exit`.

Risks: cleanup is string-evaluated in `trap`, so callers must pass valid shell fragments. Because `status=1` is the default, tests must explicitly set `status=0` before exit. Removing `$tmp.*` assumes `$tmp` is always well-formed; `_begin_fstest` sets it to `${TMPDIR:-/tmp}/$$`.

Test signals: a correctly initialized test emits `QA output created by <seq>`, has a mounted/validated test device through `init_rc`, and exits with status zero only after setting `status=0`.
