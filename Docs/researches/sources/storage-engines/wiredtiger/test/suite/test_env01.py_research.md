# sources/storage-engines/wiredtiger/test/suite/test_env01.py

## Purpose

Tests WiredTiger home-directory selection from explicit home arguments, `WIREDTIGER_HOME`, `use_environment`, and privileged `use_environment_priv`. The class/comment still use an older `test_priv01` name, but the source file is the environment test.

## Important APIs, Types, and Functions

Defines `test_priv01`, overrides connection/session setup to let each test open manually, and provides `populate_and_check`, `checkfiles`, `checknofiles`, and `common_test`.

## Control Flow

Each case creates candidate home directories, sets or unsets `WIREDTIGER_HOME`, opens WiredTiger with a home argument or config flag, writes a small table, and checks which directory received the `.wt` file. Privileged tests branch on `os.getuid() != os.geteuid()` to validate protected environment use.

## State and Persistence Behavior

Persistence is observed through filesystem placement of `test_priv01.wt`. Environment variables are reset in `finally` to avoid leaking process state between tests.

## Dependencies and Integration Points

Depends on Unix `os` APIs, `wiredtiger`, `wttest`, and the connection open wrapper. It is skipped for tiered and Windows-specific behavior is skipped in `setUp`.

## Risks and Maintenance Signals

`checknofiles` counts files in a directory but uses `os.path.isfile(nm)` against the current directory, so it relies on simple empty directory layouts. Full privileged-path coverage only occurs when run setuid/root-like.

## Test Signals

Signals are successful readback from the selected home, expected privilege error text, and file existence/nonexistence checks in explicit and environment homes.
