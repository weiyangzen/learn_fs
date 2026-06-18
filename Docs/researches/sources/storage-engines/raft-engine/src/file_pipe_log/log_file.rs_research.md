# sources/storage-engines/raft-engine/src/file_pipe_log/log_file.rs

## Purpose
Implements append-only log file writers and random-access log file readers on top of the generic filesystem abstraction, including header writing, preallocation, truncation, sync, and block reads.

## Important APIs, Types, And Functions
`build_file_writer`, `LogFileWriter`, `build_file_reader`, and `LogFileReader` are the core items. `FILE_ALLOCATE_SIZE` caps preallocation chunks at 2 MiB. Writer methods include `open`, `write_header`, `close`, `truncate`, `write`, `sync`, and `offset`; reader methods include `open`, `parse_format`, `read`, `read_to`, and `file_size`.

## Control Flow
Writer open inspects handle size. If the file is too small for the expected header or force-reset is requested, it rewinds and writes a fresh header; otherwise it seeks to the current file end. `write` calculates required capacity, attempts allocation using target-size hints, writes all bytes, and on write failure reseeks to the previous written offset so the writer remains reusable. `close` truncates fallocated zeros and syncs. Reader parse reads the maximum header length from offset zero and decodes format. `read_to` seeks only when needed and loops until the buffer is filled or EOF, retrying interrupted reads.

## State And Persistence Behavior
`LogFileWriter` tracks durable write offset and allocated capacity. It mutates file headers, payload bytes, truncation length, and sync durability. `LogFileReader` tracks its current offset as a cache over the underlying reader. Allocation may create extra zero bytes that are removed on close/truncate.

## Dependencies And Integration Points
Depends on `FileSystem`, `Handle`, `WriteExt`, `FileBlockHandle`, `LogFileFormat`, metrics, failpoints, and engine errors. It is used by file pipe log queues for appends, rewrites, recovery reads, and block lookup.

## Risks And Edge Cases
`sync` unwraps handle sync and panics on failure to avoid silent data loss. Allocation failures are logged but non-fatal, so later writes may still fail. A failpoint can skip truncate, leaving padded zeros for recovery to interpret. The fail-safe writer promise depends on successful reseek after failed writes.

## Test Signals
Signals come from file format tests, failpoint tests, engine recovery/rewrite tests, tail corruption handling, and purge/recycle tests that depend on proper truncation and header parsing.
