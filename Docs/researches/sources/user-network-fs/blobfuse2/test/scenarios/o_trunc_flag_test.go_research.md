<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go -->
# sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go

Source path: `sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go`

## Purpose
Scenario-level filesystem semantics test for `o_trunc_flag` behavior across configured blobfuse2 mountpoints.

## Important APIs, Types, And Functions
Package functions: `TestOTruncFlag`, `TestOTruncWhileWriting`, `OTruncWhileWritingHelper`, `TestOTruncWhileReading`, `OTruncWhileReadingHelper`. Types: none declared. Imports: `crypto/rand`, `io`, `os`, `path/filepath`, `testing`, `github.com/stretchr/testify/assert`.

## Control Flow
The test functions iterate over `mountpoints` initialized by `init_test.go`, perform Go/POSIX file operations on each mount, assert immediate behavior with `testify/assert`, then call shared MD5 integrity checks and cleanup helpers where applicable.

## State And Persistence
Persists test files under every mounted path and compares the final content across mounts via MD5. Shared globals from `init_test.go` provide mount roots and cleanup behavior.

## Dependencies And Integration Points
Integrates with Go's `testing` package, `testify/assert`, shared scenario globals from `init_test.go`, mounted FUSE paths, MD5 integrity helpers, and POSIX-style file operations.

## Risks
These tests are sensitive to cache coherency, remote writeback latency, and Linux filesystem semantics. Parallel tests can expose races but also make failures timing-dependent.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scenarios/o_trunc_flag_test.go -->
