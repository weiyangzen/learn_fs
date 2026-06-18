# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/seq_read_large_file_test.go

## Purpose

This test validates sequential full-file reads of a 500 MiB mounted object, including an `O_DIRECT` open path.

## Important APIs, Types, and Functions

`TestReadLargeFileSequentially` creates and copies a 500 MiB local file, opens the mounted file with `os.O_RDONLY|syscall.O_DIRECT`, reads it sequentially using `operations.ReadFileSequentially` with a 200 MiB chunk size, reads the local source with `operations.ReadFile`, and compares byte slices.

## Control Flow

The test creates the file pair, opens the mounted file, reads sequentially into memory, reads the entire local file, compares content with `bytes.Equal`, and removes the local file.

## State and Persistence Behavior

It creates a large local file and mounted object. It loads the full 500 MiB contents into memory for comparison, which creates high memory pressure. The local file is explicitly removed; bucket object cleanup is handled by package setup.

## Dependencies and Integration Points

It depends on `operations.CreateFileAndCopyToMntDir`, `operations.ReadFileSequentially`, `operations.ReadFile`, package constants, and setup file permissions. It exercises the kernel/direct-read path as controlled by mount flags.

## Risks and Edge Cases

`O_DIRECT` has platform and alignment constraints, so helper implementations must respect direct I/O requirements. Reading the entire file into memory can be expensive. The test catches content errors but not partial performance regressions.

## Test Signals

Passing signal is exact equality between sequentially read mounted content and the local source. Failures suggest direct I/O, sequential buffering, large chunk, or EOF handling bugs.
