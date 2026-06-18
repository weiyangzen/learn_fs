# sources/test-tools/syzkaller/pkg/db/db_test.go

This file tests the corpus DB implementation's persistence, mutation, recovery, memory-saving mode, and crafted-input bounds checks.

Core tests include `TestBasic` for save/flush/reopen, `TestModify` for updates and deletes, `TestLarge` for many compressed records, `TestDiscardData` for nil in-memory values plus compaction reread, `TestOpenInvalid` and `TestOpenCorrupted` for repair-mode behavior, and `TestOpenInaccessible` for permission failures when not root. `TestDecompressionBombValLen` verifies decompressed values over `maxValLen` are rejected, and `TestOversizeKeyLen` verifies oversized key lengths fail before large allocation.

State is temporary database files created through `tempFile` and deleted after tests. Dependencies are `osutil`, binary encoding helpers from `db.go`, flate serialization through production code, random data for large records, and testify assertions.

Integration signal is strong for durability and security boundaries: the tests assert that repair mode returns a non-nil DB with recovered records on corruption, that atomic compaction preserves desired records, and that hostile record lengths do not cause OOM. Risks include nondeterministic compression sizes, root-specific permission semantics, and test expectations tied to the current compaction threshold.
