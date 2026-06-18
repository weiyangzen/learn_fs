# sources/sync-backup/kopia/internal/gather/gather_bytes_test.go

Purpose: exhaustively tests logical byte operations over empty, nil, single-slice, and multi-slice `Bytes` values.

Important APIs/types/functions: `Bytes.Length`, `Reader`, `ToByteSlice`, `WriteTo`, `AppendSectionTo`, `ReadAt` via `io.ReaderAt`, `WriteBuffer`, `ErrInvalidOffset`, `iotest.TestReader`, and `testutil.EnsureType`.

Control flow: `TestGatherBytes` iterates many slice layouts and all start/end section ranges, verifying appended sections equal the corresponding contiguous subslice and write errors propagate. Reader tests build large `WriteBuffer` contents around allocator chunk boundaries and run `iotest.TestReader`. Error-response tests cover negative offsets, huge offsets, zero-length reads, and variable read buffer sizes.

State/persistence behavior: tests are in-memory and rely on `WriteBuffer` chunk allocation. `TestGatherBytesPanicsOnClose` intentionally closes a buffer then verifies exposed `Bytes` panic on use, documenting lifetime rules.

Dependencies/integration: exercises gather with `WriteBuffer`, `testing/iotest`, `testutil`, and `pkg/errors`. It is the main regression suite for byte-slice boundary handling.

Risks/test signals: broad boundary coverage catches EOF and slice-index bugs. The tests assume the default allocator chunk size for some cases, so allocator changes may require test adjustment.
