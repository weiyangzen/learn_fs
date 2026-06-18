# sources/sync-backup/kopia/repo/hashing/blake3_hashes.go

Purpose: registers Kopia's BLAKE3 keyed hashing algorithms with full 256-bit and truncated 128-bit output lengths.

Important APIs/types/functions: `newBlake3`, `blake3KeySize`, and the package `init` registrations for `BLAKE3-256` and `BLAKE3-256-128`.

Control flow: `newBlake3` derives a 32-byte BLAKE3 key when the supplied repository secret is shorter, then creates a keyed BLAKE3 hash. Registration wraps that constructor with `truncatedKeyedHashFuncFactory`.

State/persistence behavior: the algorithm name and output length become part of repository format parameters. The derived-key context string is a compatibility-sensitive constant.

Dependencies/integration: depends on `github.com/zeebo/blake3` and the shared hashing registry in `hashing.go`.

Risks/test signals: key handling must remain deterministic across releases or repositories become unreadable. Generic hashing tests exercise output stability and data separation across all registered algorithms.
