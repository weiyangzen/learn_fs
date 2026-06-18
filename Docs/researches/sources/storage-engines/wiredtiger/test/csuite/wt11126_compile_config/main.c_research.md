# sources/storage-engines/wiredtiger/test/csuite/wt11126_compile_config/main.c

Purpose: this program is both a correctness test and benchmark for WiredTiger compiled configuration strings, specifically for `WT_SESSION.begin_transaction`. It compares formatting on every call, choosing prebuilt strings, binding values into one compiled configuration, choosing among many compiled configurations, and null configuration.

Important APIs, types, and functions: key APIs are `WT_CONNECTION::compile_configuration`, `WT_SESSION::bind_configuration`, `WT_SESSION::begin_transaction`, and `WT_SESSION::rollback_transaction`. It also inspects `WT_SESSION_IMPL` and `WT_TXN` flags to verify config effects. `THREAD_OPTS` passes shared compiled config pointers and timing buffers to benchmark threads. Initialization helpers include `begin_transaction_medium_init`, `begin_transaction_fast_init`, and `begin_transaction_fast_alternate_init`. `do_config_run` runs one variant for `N_CALLS`.

Control flow: `main` parses test options and thread count, opens WiredTiger, initializes all precomputed/compiled configurations, starts benchmark threads, waits for them, then prints nanoseconds per begin/rollback pair and speed relative to baseline. Each thread loops `N_RUNS` times across all variants. For the first run, non-null variants verify that internal transaction flags match random `ignore_prepare`, `roundup_timestamps`, and `no_timestamp` values.

State and persistence behavior: no user table is created; the persistent database is just a temporary WiredTiger home used to own a connection and sessions. The main state under test is compiled configuration lifetime across the connection and per-session transaction flags after begin/rollback cycles.

Dependencies and integration points: it depends on WiredTiger's internal transaction flag definitions and compiled configuration API. It is useful as a performance benchmark but has assertions that make it a correctness test as well.

Risks and test signals: benchmark numbers are environment-sensitive, but pass/fail comes from API return checks and flag assertions. Risk areas include compiled config lifetime, binding type mismatches, and internal flag changes not reflected in the test.
