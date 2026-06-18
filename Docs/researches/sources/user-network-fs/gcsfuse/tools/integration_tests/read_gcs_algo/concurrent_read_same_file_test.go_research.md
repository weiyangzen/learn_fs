# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/concurrent_read_same_file_test.go

## Purpose

This file stress-tests concurrent random reads from the same mounted file and compares every read against a local disk copy. It targets the GCSFuse read algorithm under shared-file-handle-independent workloads.

## Important APIs, Types, and Functions

`TestReadSameFileConcurrently` creates a 30 MiB file, copies it into the mount, and starts three goroutines through `errgroup.Group`. `readAndCompare` opens the mounted file read-only, performs five `ReadAt` calls at a supplied offset and chunk size, reads the same bytes from the local disk file, and compares byte slices with `bytes.Equal`.

## Control Flow

The test creates one source/mounted file pair, chooses a random offset for each goroutine, and has every goroutine call `readAndCompare` with a 5 MiB chunk size. `readAndCompare` treats `io.EOF` as non-fatal because a random offset near EOF may return a short read. It then reads the matching local chunk with `operations.ReadChunkFromFile` and fails the test if content differs.

## State and Persistence Behavior

The test persists a generated file on local disk and in the mounted bucket prefix through helper APIs. It has no explicit cleanup in this file, relying on shared integration helpers and package cleanup. The mounted file is opened separately per goroutine, which isolates file offsets while exercising shared backend/cache behavior.

## Dependencies and Integration Points

It depends on `read_gcs_algo` package constants from `read_gcs_algo_test.go`, `operations.CreateFileAndCopyToMntDir`, `operations.OpenFileAsReadonly`, `operations.ReadChunkFromFile`, and `golang.org/x/sync/errgroup`. It integrates with the package mount harness that supplies the bucket and flags.

## Risks and Edge Cases

Random offsets are chosen with `rand.Int64N(fileSize)` but a 5 MiB chunk may extend beyond EOF; both mounted and local helper behavior must produce comparable buffers for short reads. The goroutines call `t.Fatalf` from worker goroutines, which is common in tests but can make failure reporting abrupt. `errgroup` itself does not receive real errors from the helper because fatal exits happen through `testing.T`.

## Test Signals

Passing signal is byte-for-byte equality across five repeated random reads in each concurrent goroutine. Failures indicate concurrency bugs in read buffering, range handling, cache reuse, or mounted-file consistency against local disk.
