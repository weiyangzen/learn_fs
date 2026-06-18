# sources/storage-engines/tikv/components/engine_traits_tests/src/delete_range.rs

Purpose: Tests invalid CF behavior for range deletes.

Important APIs and control flow: Opens a default-only engine, calls `delete_range_cf("bogus", b"a", b"b")`, and expects panic/error recovery through `panic_hook::recover_safe`.

State, persistence, and dependencies: No data should be persisted; only CF lookup/error behavior is exercised.

Integration points, risks, and test signals: Signals that implementations reject unknown CFs for range deletes rather than silently applying to default or succeeding. The test expects an unwind path, so implementations that return ordinary errors may need alignment with existing test expectations.
