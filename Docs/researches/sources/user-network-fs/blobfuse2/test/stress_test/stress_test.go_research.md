<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go -->
# sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go

Source path: `sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go`

## Purpose
Parallel upload/download stress test for mounted storage with small, big, and huge file profiles.

## Important APIs, Types, And Functions
Package functions: `downloadWorker`, `uploadWorker`, `BytesCount`, `stressTestUpload`, `stressTestDownload`, `TestStress`, `StressSmall`, `StressBig`, `StressHuge`, `TestMain`. Types: `workItem`. Imports: `crypto/rand`, `flag`, `fmt`, `os`, `path/filepath`, `strconv`, `testing`, `time`.

## Control Flow
Worker goroutines consume directory/file creation or read jobs from channels. `TestStress` runs small, big, and huge profiles; `TestMain` parses mount path and quick-mode flags, prepares the stress root, and cleans up afterward.

## State And Persistence
Creates many directories and files below the selected mount path, reads them back, logs throughput, and removes the stress tree after each profile and at process exit.

## Dependencies And Integration Points
Integrates with Go's `testing` package, host filesystem calls, configured mounted FUSE paths, worker goroutines/channels, and throughput logs.

## Risks
The full mode allocates and writes very large buffers, including 2 GiB files, so memory, disk, network, and service throttling can dominate results. The global `noOfWorkers` is mutated by small profiles and may affect later profiles.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/stress_test/stress_test.go -->
