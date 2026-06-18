# sources/storage-engines/tikv/tests/failpoints/cases/mod.rs

Purpose: central module manifest for failpoint integration tests.

Important APIs and functions: declares all failpoint case modules, including the subset files researched here and many additional cases such as local read, merge, rawkv, storage, titan, transaction, ttl, unsafe recovery, and witness.

Control flow: compile-time test module registration only. The Rust test harness discovers `#[test]` and `#[test_case]` functions in children.

State and persistence: none directly.

Dependencies and integration: this file is the integration point between `tests/failpoints` and individual failure-injection scenarios.

Risks and test signals: missing a `mod` declaration disables an entire failpoint file. Additions here can increase failpoint suite runtime and global failpoint interactions.
