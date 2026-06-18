# sources/object-store/minio/cmd/erasure-encode.go

Purpose: Streams object bytes into erasure-coded shard writers while enforcing write quorum. This is the write-side counterpart to decode/heal.

Important APIs/types/functions: `multiWriter` stores shard writers, write quorum, and per-writer errors. `multiWriter.Write` writes each shard block, tracks nil writers as `errDiskNotFound`, handles short writes, disables failed writers, and uses `reduceWriteQuorumErrs` for quorum failure reporting. `Erasure.Encode` reads full erasure blocks from `src`, encodes each block with `EncodeData`, writes shards through `multiWriter`, handles empty objects by writing empty data/parity files, and returns total source bytes consumed.

Control flow and state: The write loop uses `io.ReadFull` over the provided block buffer. EOF and unexpected EOF are accepted as final-block conditions. Writer error state is retained across blocks so a failed shard writer is skipped for the rest of the object. Persistence occurs through supplied `io.Writer`s, typically bitrot writers over storage disks.

Dependencies and integration points: Uses `EncodeData` from `erasure-coding.go`, quorum reducers from metadata utilities, object operation ignored errors, and bitrot writer implementations passed by callers such as PutObject and tests.

Risks: Quorum is caller-supplied and must match object semantics. A writer that succeeds partially is disabled after `io.ErrShortWrite`. Empty-object behavior intentionally writes empty shard files, which callers must preserve. The returned error wraps offline disk counts for operational visibility.

Test signals: Encode tests cover zero-byte objects, varied layouts/block sizes/offsets, faulty writers, and quorum failure thresholds; benchmarks cover common performance layouts.
