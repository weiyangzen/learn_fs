# sources/object-store/minio/cmd/bitrot-streaming.go

This file implements streaming bitrot protection for `HighwayHash256S`, where every shard is stored as `hash || data` instead of maintaining one whole-file checksum. It provides writer and reader implementations used by the generic bitrot factory functions.

`streamingBitrotWriter` wraps an `io.WriteCloser`, hash, shard size, optional close wait group, pooled byte buffer, and finished flag. `Write` rejects empty writes as no-ops, rejects writes after the final short shard, rejects buffers larger than the shard size, hashes the provided shard, writes hash bytes followed by data, and propagates errors via `closeWithErr`. `Close` closes the underlying writer, waits for the async disk writer if present, and returns the pooled buffer.

`newStreamingBitrotWriterBuffer` is an in-memory/test helper. `newStreamingBitrotWriter` obtains a buffer from `globalBytePoolCap`, creates a blocking ring buffer wrapped in a deadline writer, starts a goroutine that computes the total on-disk size when object length is known, and calls `disk.CreateFile` with the ring-buffer reader. This decouples shard hashing from disk writes while preserving close ordering with a wait group.

`streamingBitrotReader.ReadAt` requires offsets aligned to shard size and sequential access. On the first read it opens a disk stream at the translated offset `(offset/shardSize)*hashSize + offset`, or uses in-memory data. Each read consumes stored hash bytes and the requested data, recomputes the hash, compares it, and advances `currOffset`. `Close` drains and closes the stream for connection reuse.

Dependencies include `StorageAPI`, MinIO deadline writer and ring buffer utilities, HTTP body draining, global byte pools, and hash algorithms from `bitrot.go`. Risks are strict offset/sequential assumptions, final-shard detection based on short writes, race potential around async writer close, and correctness of translated offsets and `tillOffset` sizing.
