# sources/security-integrity/gocryptfs/internal/contentenc/bpool.go

Purpose: This file implements a fixed-size byte-slice pool used by content encryption to reduce allocations on hot read/write paths.

Important APIs and types: `bPool` embeds `sync.Pool` and records the required slice length. `newBPool`, `Put`, and `Get` create, return, and retrieve fixed-size buffers.

Control flow and state: `Put` expands slices to capacity and panics if length does not match the pool's configured size. `Get` asserts returned slice length. Pool contents are transient runtime memory.

Dependencies and integration points: Used by `ContentEnc` for ciphertext blocks, plaintext blocks, and request-sized buffers.

Risks and test signals: Returning a wrong-sized or still-referenced buffer can corrupt encryption operations. Panics protect internal misuse. Signals include allocation benchmarks and tests that exercise read/write paths without pool-size panics.
