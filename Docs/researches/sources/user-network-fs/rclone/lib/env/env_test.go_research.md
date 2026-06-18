# sources/user-network-fs/rclone/lib/env/env_test.go

Source read signal: reviewed complete local file (32 lines, sha256 4ab874ec54b927de).

Purpose: Tests `ShellExpand` path and environment expansion semantics.

Important APIs/types/functions: `TestShellExpand` sets `EXPAND_TEST`, obtains the home directory with `homedir.Dir`, and checks table-driven expected values.

Control flow: The test sets and defers unsetting the environment variable, then compares empty input, bare `~`, leading `~/...`, non-leading `~`, and combined tilde/env expansion.

State and persistence behavior: Temporarily mutates the process environment and uses `t.Temp`-free local state only.

Dependencies and integration points: Uses `filepath.FromSlash` for platform-neutral expectations, `testify/assert`, and `require`.

Risks and test signals: Good coverage for `ShellExpand`; there is no direct test for `CurrentUser`, so fallback behavior remains less protected.
