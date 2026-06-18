<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go -->
# sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go

## Purpose
Go test suite for measuring large file creation times on a mount path.

## Important APIs, Types, and Functions
Globals `mntPath`, `n`, and `sizes` configure benchmark directory, repetitions, and GB sizes. `createSingleFile` allocates a buffer of requested size and writes it with `os.WriteFile`. `TestCreateSingleFiles` repeats each size, removes files, and logs mean/stddev using `montanaflynn/stats`. `TestMain` parses flags `mnt-path`, `n`, and `sizes`, prepares the benchmark directory, and cleans up afterward.

## Control Flow and State
The suite writes test files under `<mnt-path>/benchmark`, removes each after timing, and removes the base directory at exit. It mutates global config from flags.

## Dependencies and Integration Points
Depends on `testify/suite` and `github.com/montanaflynn/stats`. Intended for real Blobfuse2 mount paths and excluded under `unittest`.

## Risks and Edge Cases
Allocating full file-size buffers can consume multiple GiB of RAM. Errors during file creation are logged but durations are still appended, potentially skewing metrics. This is a test-style benchmark, not `go test -bench`.

## Test Signals
Logs mean and standard deviation per file size. It measures create/write time but does not validate content or upload completion beyond `os.WriteFile` returning.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/benchmark_test/benchmark_test.go -->
