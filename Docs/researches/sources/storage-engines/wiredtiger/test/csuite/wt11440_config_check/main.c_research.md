# sources/storage-engines/wiredtiger/test/csuite/wt11440_config_check/main.c

Purpose: this benchmark-style correctness test compares two caller-side strategies for `begin_transaction` configuration strings: formatting a string every call and choosing among preformatted strings. It validates that both produce the same transaction flag effects for a MongoDB-like four-variable configuration.

Important APIs, types, and functions: it uses `WT_SESSION::begin_transaction`, `WT_SESSION::rollback_transaction`, internal `WT_SESSION_IMPL` and `WT_TXN` flag checks, random config selection, and a table of implementation variants. `begin_transaction_base` formats with `__wt_snprintf`. `begin_transaction_advance_format_init` prepares all 24 combinations of `ignore_prepare`, `roundup_timestamps.prepared`, `roundup_timestamps.read`, and `no_timestamp`; `begin_transaction_advance_format` selects one.

Control flow: `main` opens a temporary connection/session, initializes variant data, then alternates variants for `N_RUNS`. `do_config_run` runs `N_CALLS` begin/rollback pairs with random config booleans, optionally checks internal flags on the first run, and accumulates elapsed nanoseconds. The program prints total and per-call timing plus speed relative to the base variant.

State and persistence behavior: the database home exists only to hold a WiredTiger connection and session. There is no application table state. The relevant mutable state is the active transaction configuration flags that are reset by rollback after each call.

Dependencies and integration points: it depends on test utility setup, `statistics_log`, internal transaction flags, and stable configuration option names for `begin_transaction`.

Risks and test signals: timing is not deterministic, so correctness assertions are the meaningful test signal. If config parser semantics or internal flag names change, this test needs updates. A passing run completes all calls and prints benchmark lines.
