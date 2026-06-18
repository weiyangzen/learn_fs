# Research: sources/storage-engines/tikv/components/test_util/src/runner.rs

## sources/storage-engines/tikv/components/test_util/src/runner.rs

Purpose: bridges Rust's unstable custom test framework APIs with TiKV test setup and optional failpoint lifecycle management.

Important APIs are `run_tests`, `TestHook`, `run_test_with_hook`, `clear_failpoints`, and `run_failpoint_tests`. `run_test_with_hook` calls `setup_for_ci`, wraps each static test or bench in a dynamic function that creates a `CaseLifeWatcher`, invokes hook setup before the case, and relies on `Drop` for teardown and end logging. It then calls `test_main`. `FailpointHook` manages a thread-local `fail::FailScenario` for each case.

State is thread-local failpoint scenario storage plus per-case watcher names/hooks. Persistence is none, but failpoints affect global test behavior while active. Dependencies are the nightly `test` crate exposed by the crate root, `fail`, environment args, and logging macros.

Risks include nightly API instability, failpoint cleanup during panics requiring explicit `clear_failpoints`, unsupported dynamic test function variants causing panic, and hook clone/send requirements. Test signals are failpoint tests not leaking failpoints across cases and logs showing case start/end around each wrapped test.
