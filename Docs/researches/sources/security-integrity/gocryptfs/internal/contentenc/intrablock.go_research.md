# sources/security-integrity/gocryptfs/internal/contentenc/intrablock.go

Purpose: This file implements conversions between plaintext offsets/ranges and cipher block ranges within gocryptfs files.

Important APIs and functions: It provides helpers to split a byte range into block number, intra-block offset, skip, and length components, plus conversions between plaintext and ciphertext sizes/offsets accounting for header and per-block overhead.

Control flow and state: Functions are pure arithmetic over offsets, lengths, block sizes, and overhead. No state is persisted.

Dependencies and integration points: Used by read/write paths, fsck, and tests to map FUSE requests to encrypted block reads/writes.

Risks and test signals: Off-by-one errors can corrupt reads/writes at block boundaries or EOF. Signals include boundary tests for zero length, unaligned ranges, multi-block ranges, and size conversion round trips.
