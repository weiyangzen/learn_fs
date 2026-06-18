# sources/sync-backup/casync/test/test-cadigest.c

Purpose: verifies digest implementations and known output vectors.

Important APIs/types/functions: `test_speed` benchmarks or exercises each digest type; `main` checks SHA-256 and SHA-512/256 byte-for-byte outputs after specific writes.

Control flow/state: allocates `CaDigest`, writes data incrementally, reads final digest, and compares to embedded expected byte arrays.

Dependencies/integration: covers digest type selection, reset/write/read/finalization, and configured crypto backends.

Risks/test signals: strong regression signal for digest correctness, though performance output is diagnostic. Backend availability can affect which digest types are tested.

Source research group: `subset-b-009122`.
