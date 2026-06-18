# sources/sync-backup/kopia/repo/hashing/hashing.go

Purpose: provides the hashing registry and factory helpers used to produce repository content ID hash functions from repository format parameters.

Important APIs/types/functions: `Parameters`, `HashFunc`, `HashFuncFactory`, `Register`, `SupportedAlgorithms`, `DefaultAlgorithm`, `CreateHashFunc`, `truncatedHMACHashFuncFactory`, and `truncatedKeyedHashFuncFactory`.

Control flow: algorithm-specific files register factories at init time. `CreateHashFunc` looks up the configured name, initializes the algorithm with `GetHmacSecret`, validates non-nil output, and returns a function that writes `gather.Bytes` into a pooled hash and appends truncated digest bytes to the caller-provided output slice.

State/persistence behavior: global `hashFunctions` is process-local registry state; repository persistence stores only the algorithm name and secret. `sync.Pool` reduces allocations but requires each hash to be reset before reuse.

Dependencies/integration: used by repository initialization and remote/direct content managers for content ID generation. It relies on `gather.Bytes.WriteTo` and `crypto/hmac` for HMAC algorithms.

Risks/test signals: registry mutation is global and not locked after init, so dynamic registration would need care. Incorrect truncation or secret handling would corrupt content addressing. Tests exercise every registered algorithm for deterministic output and distinction between different data.
