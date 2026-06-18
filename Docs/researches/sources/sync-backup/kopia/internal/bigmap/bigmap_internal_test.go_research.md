## sources/sync-backup/kopia/internal/bigmap/bigmap_internal_test.go

Purpose: tests and benchmarks the unexported internal hash table directly.

Important APIs/types/functions: `TestInternalMap`, `TestGrowingMap`, `TestGrowingSet`, `TestErrors`, `TestPanics`, `TestMapWithoutValue`, `sha256Key`, and internal/sync.Map benchmarks.

Control flow, state, and persistence: tests insert keys and values, force growth and segment rollover with small options, verify previous entries during insertion, and assert panics for invalid key lengths or values when disabled. Benchmarks compare internal map behavior against `sync.Map`.

Dependencies and integration points: uses test logging, SHA-256 key generation, and internal constructors.

Risks and test signals: strong coverage for append-only growth and no-value mode. It does not force mmap failure paths or extremely large table-size indexes.
