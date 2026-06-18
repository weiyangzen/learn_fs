# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/concurrent_read_files_test.go

## Purpose

This file validates concurrent reads of multiple large files through a mounted GCSFuse directory. It targets large-object throughput and correctness when several 500 MiB objects are created and read at the same time.

## Important APIs, Types, and Functions

The file defines random file names `FileOne`, `FileTwo`, and `FileThree`, plus `NumberOfFilesInLocalDiskForConcurrentRead`. `TestReadFilesConcurrently` creates a package test directory, concurrently creates/copies three local files to the mount, registers local-file cleanup, and concurrently reads each mounted file with `operations.ReadAndCompare`.

## Control Flow

An `errgroup.Group` first starts three creation goroutines, each selecting a local path under `$HOME`, a mount path under the test directory, and creating/copying a 500 MiB file. After creation succeeds, a cleanup closure is registered for each local file. A second errgroup runs one full-file read comparison per file.

## State and Persistence Behavior

The test creates three large local files and three mounted bucket objects. Local files are removed via `t.Cleanup`; mounted content is handled by package-level test-directory cleanup. Arrays of paths are shared across goroutines with distinct indices.

## Dependencies and Integration Points

It depends on package constants from `read_large_files_test.go`, `setup.SetupTestDirectory`, `setup.GenerateRandomString`, `operations.CreateFileOnDiskAndCopyToMntDir`, and `operations.ReadAndCompare`. It runs under the read-large-files mount matrix, including file-cache variants.

## Risks and Edge Cases

The test is resource-intensive: it writes and reads roughly 1.5 GiB of test data. It depends on available disk, mount bandwidth, and timeout budget. Although index capture is handled explicitly, calls into `testing.T` from goroutines can produce abrupt failure behavior. Parallel creation and read may expose cache capacity pressure under file-cache configurations.

## Test Signals

Passing signal is full byte equality for all three 500 MiB mounted files against their local sources under concurrent reads. Failures may indicate race conditions, large-range read bugs, cache eviction problems, or environment resource exhaustion.
