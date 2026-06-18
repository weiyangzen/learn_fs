# sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs

Purpose: Integration-tests `StaticDrop` behavior that unit tests cannot observe: whether registered static values are dropped when a process exits via `std::process::exit`, whether all entries run, and whether panic in one `Drop` does not stop siblings.

Important APIs and types: Uses `StaticDrop`, `LazyLock`, `TempDir`, `Command`, `Output`, environment variables `STATIC_DROP_PROCESS_EXIT_CHILD` and `STATIC_DROP_SENTINEL_DIR`, plus sentinel helper types `DropSentinel` and `PanicAfterWritingSentinel`.

Control flow: Each test has parent and child roles. The parent creates a temp directory, spawns the same test binary filtered to one exact test with child env vars, and inspects stdout or sentinel files after the child exits. The child initializes one or more lazy statics containing `StaticDrop` wrappers and exits with `process::exit(0)`. The panic test writes a sentinel and panics during one destructor; the parent still expects all sentinels and a successful child status.

State and persistence behavior: Parent-owned temp directories and child-written sentinel files are the observable persistence mechanism. The single-tempdir test prints the child tempdir path before exit, and the parent asserts that directory has been removed by `TempDir::drop`.

Dependencies and integration points: Requires the crate `testutils` feature. It validates the `dtor(at_binary_exit)` path in `static_drop.rs`, especially with libtest-style process exits.

Risks: The tests rely on spawning the current test executable and exact test-name filtering, so harness behavior matters. They assume filesystem side effects are visible after child termination. The child role returns `!` through `process::exit`, so forgetting an early return in parent/child branching would run parent assertions in the child.

Test signals: Child exit success, missing tempdir after process exit, sentinel files `a`, `b`, and `c` existing for multiple entries, and all sentinels still existing when one destructor panics.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/tests/static_drop_process_exit.rs` completely for this pass (233 lines, 8110 bytes).
