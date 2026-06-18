# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFile.cpp

## Purpose
`AsyncFile.cpp` implements common support for async file tester workloads: deterministic random byte generation, aligned buffer allocation, temporary file cleanup, shared workload options, and a default success check.

## Important APIs, Types, and Functions
- `RandomByteGenerator`: precomputes a 16 MiB deterministic random buffer and writes output by XORing two random aligned slices.
- `AsyncFileWorkload::_PAGE_SIZE`: 4096-byte alignment constant.
- `AsyncFileWorkload::AsyncFileWorkload`: enables only client 0 and reads `testDuration`, `unbufferedIO`, `uncachedIO`, `fillRandom`, and `fileName`.
- `AsyncFileWorkload::allocateBuffer`: creates an `AsyncFileBuffer` with alignment based on `unbufferedIO`.
- `AsyncFileBuffer`: allocates/frees normal or aligned memory and zero-fills it.
- `AsyncFileHandle`: wraps `IAsyncFile`, path, and temporary cleanup behavior.

## Control Flow
Workload subclasses call `allocateBuffer` and the inline `openFile` actor declared in `AsyncFile.h`. Random data generation selects two distinct offsets into the precomputed buffer, XORs 64-bit words, and writes them into the caller's buffer. `AsyncFileHandle` deletion cleans up temporary files when the reference-counted handle is destroyed.

## State and Persistence Behavior
`AsyncFileWorkload` stores `fileHandle`, `fileSize`, and `path`. `AsyncFileHandle` owns file cleanup if `temporary` is true. `AsyncFileBuffer` owns heap memory only. This file does not mutate file contents directly except through helper data generation and destructors; actual IO is performed by subclasses and `openFile`.

## Dependencies and Integration Points
The file depends on tester workload infrastructure, Flow actor support, and `AsyncFile.h`. It is shared by `AsyncFileCorrectness`, `AsyncFileRead`, and `AsyncFileWrite`, and integrates indirectly with `IAsyncFile` via the header declarations.

## Risks
`RandomByteGenerator::~RandomByteGenerator` uses `delete` for an array allocated with `new char[]`, which is a memory-management issue worth reviewing. `writeRandomBytesToBuffer` assumes 8-byte aligned buffers and byte counts. Allocation failure logs `TestFailure` and asserts rather than returning a workload-level failure. Temporary cleanup ignores delete errors.

## Test Signals
No direct tests are present. Allocation failure emits `TraceEvent(SevError, "TestFailure")`. The support code is indirectly exercised by async file correctness, read, and write workloads.
