
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/hidrivehash_test.go

## Purpose
This file validates the custom HiDrive hash implementation against documentation-derived vectors and important hash.Hash behaviors.

## Important APIs, Types, And Control Flow
The tests define vector tables for position-embedded level additions, level writes, and full HiDrive hashes over generated repeated data/null-byte patterns. `TestLevelAdd`, `TestLevelWrite`, `TestLevelIsFull`, reset/size/block-size tests, marshal/unmarshal tests, and invalid encoding tests cover `level`. `TestWrite`, `TestReset`, `TestBinaryMarshaler`, `TestInvalidEncoding`, and `TestSum` cover `hidriveHash`. Helpers include an `infiniteReader` and `writeInChunks` to feed the same logical data with different physical write chunk sizes.

## State And Persistence
Tests persist no external state. They check in-memory hash state before and after reset and binary marshal/unmarshal.

## Dependencies And Integration Points
The tests import the public `hidrivehash` package and its internal `LevelHash` interface to validate level-specific methods. They use `testify/assert` for expectations and Go `encoding` interfaces for marshal checks.

## Risks And Test Signals
The suite strongly covers deterministic hash values, all-null content, non-block-aligned inputs, level capacity, write chunk independence, and state round trips. It only lightly covers invalid binary encodings; malformed length fields in otherwise long encodings are not exhaustively fuzzed. It does not benchmark large inputs or concurrency, which is acceptable because hash instances are not concurrency-safe.
