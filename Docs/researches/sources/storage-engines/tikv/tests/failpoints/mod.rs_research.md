# sources/storage-engines/tikv/tests/failpoints/mod.rs

See the grouped report section in `Docs/researches/groups/subset-b-008947_research.md` for the full source-aligned research. Summary: this crate root enables nightly features, installs `test_util::run_failpoint_tests` as the custom test runner, imports `slog_global` macros, sets recursion limit, and exposes the `cases` module. Its risk is harness-level: feature gates, macro imports, and runner changes affect all failpoint cases.
