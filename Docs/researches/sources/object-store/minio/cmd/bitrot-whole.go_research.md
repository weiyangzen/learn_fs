# sources/object-store/minio/cmd/bitrot-whole.go

This file implements whole-file bitrot protection for non-streaming algorithms. Instead of storing per-shard hashes in the object stream, it appends raw bytes to disk while maintaining a hash over the whole written content, then verifies reads using a `BitrotVerifier`.

`wholeBitrotWriter` holds a `StorageAPI`, target volume, file path, shard size, and embedded `hash.Hash`. `Write` appends bytes to the disk file through `disk.AppendFile`, then writes the same bytes into the hash and returns the full input length. `Close` is a no-op. `newWholeBitrotWriter` constructs the writer with `algo.New()`.

`wholeBitrotReader` holds disk location, a verifier containing algorithm and expected sum, a `tillOffset`, and an internal verified buffer. On the first `ReadAt`, it allocates `tillOffset-offset` bytes and calls `disk.ReadFile` with the verifier. Subsequent reads copy out of the verified buffer and shrink it. If the requested buffer is larger than remaining verified data, it returns `errLessData`.

State is local to the reader/writer, but the design relies on the storage layer honoring `BitrotVerifier` during `ReadFile`. The reader caches verified data after the first read, so it assumes the caller reads forward through that cached slice. Dependencies include `StorageAPI`, `context.TODO`, Go `hash` and `io`, and bitrot algorithm definitions.

Risks include no explicit close flushing, memory use proportional to `tillOffset-offset`, limited random-access behavior after the initial read, and reliance on callers passing the exact checksum from `bitrotWriterSum`. Test coverage comes from `bitrot_test.go`, which writes and reads shard-sized chunks for all registered algorithms.
