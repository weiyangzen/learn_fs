# sources/test-tools/cthon04/special/bigfile.c

## Purpose
`bigfile.c` writes, syncs, closes, reopens, and verifies a large file to expose NFS and filesystem failures around dirty cache pressure, large-range commits, stale attributes, and ENOSPC/EDQUOT propagation. When compiled with `MMAP`, it repeats the exercise through shared mappings.

## Important APIs, Types, and Functions
Important functions are `main()`, `write_read()`, optional `write_read_mmap()`, `verify()`, `dump_buf()`, `io_error()`, and `testval()`. Runtime state is `file_size`, `filename`, `buffer_size`, and optional `pagesize`.

## Control Flow and State
`main()` accepts `-s size_in_MB`, creates/truncates the target, calls buffered I/O verification, optionally calls mmap verification, and unlinks the file. `write_read()` fills each 8192-byte buffer with a deterministic byte pattern, calls `fsync()`, closes/reopens, seeks every buffer offset, and verifies each block. The mmap path truncates, maps the whole file writable, fills page-sized regions, `msync()`s, unmaps, then maps each page read-only for verification.

## Persistence and Dependencies
Persistent state is the test file until final unlink or until non-space errors intentionally leave it for inspection; space/quota failures unlink before exit. Dependencies: POSIX file I/O, `fsync`, `ftruncate`, `mmap`/`msync`/`munmap` when enabled, `errno`, and `../tests.h` for legacy prototypes/macros.

## Integration Points, Risks, and Test Signals
Integration is the special large-file test. Risks include truncating/removing the named file, using `long`/`int` counts for large sizes, only testing whole buffer/page multiples, full-file mappings that may exceed address space, and treating ENOSPC as a warning while still returning failure. Test signals are no verify dump, successful reopen reads, clean unlink, and meaningful Warning/Error distinction on storage exhaustion.
