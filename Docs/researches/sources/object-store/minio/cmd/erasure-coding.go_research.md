# sources/object-store/minio/cmd/erasure-coding.go

Purpose: Wraps Reed-Solomon erasure coding parameters and shard math for MinIO object data. It centralizes construction, shard sizing, encode/decode primitives, and a startup self-test that detects incompatible erasure algorithm behavior.

Important APIs/types/functions: `Erasure` stores a lazy `reedsolomon.Encoder` factory plus `dataBlocks`, `parityBlocks`, and `blockSize`. `NewErasure` validates shard counts, rejects more than 256 total shards, and creates the encoder lazily with `WithAutoGoroutines`. `EncodeData` splits and encodes a block into data/parity shards. `DecodeDataBlocks` reconstructs only missing data shards, with a zero-length fast path. `DecodeDataAndParityBlocks` reconstructs all shards. `ShardSize`, `ShardFileSize`, and `ShardFileOffset` translate object/block offsets to shard-file sizing. `erasureSelfTest` hashes known encoded outputs and reconstructs a deleted shard across many data/parity configurations.

Control flow and state: The only persistent state is the in-memory lazy encoder captured behind `sync.Once`. The self-test is process-startup validation: on mismatch it writes diagnostics and uses `logger.Fatal`, preventing server startup rather than risking data corruption.

Dependencies and integration points: Depends on `github.com/klauspost/reedsolomon`, `xxhash`, MinIO block-size constants, erasure algorithm enums, and logger fatal behavior. Encode/decode/heal stream implementations call this wrapper for block-level operations.

Risks: The lazy encoder closure shares the outer `err` variable from `NewErasure`; errors are expected to be impossible after earlier validation and become panics inside `Once`. Shard offset math is critical for ranged reads and last-block handling. Any upstream Reed-Solomon behavior change will trip the self-test.

Test signals: Direct tests are in encode/decode/heal suites, while `erasureSelfTest` is an internal runtime safety net with known hashes.
