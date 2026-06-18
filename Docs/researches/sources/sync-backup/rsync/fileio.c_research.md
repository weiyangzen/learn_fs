# sources/sync-backup/rsync/fileio.c

## Purpose
Provides low-level file IO helpers for buffered writes, sparse-file creation/update, matched-data skipping for in-place transfers, and mmap-like sliding-window reads implemented with `read()`.

## Important APIs, Types, and Functions
`write_file()` writes all requested bytes, using sparse handling when `sparse_files > 0` and an internal write buffer otherwise. `flush_write_file()` drains the write buffer. `skip_matched()` advances over matching in-place data. `sparse_end()` finalizes sparse writes and truncation/hole punching. `map_file()`, `map_ptr()`, and `unmap_file()` manage `struct map_struct` windows. Static `write_sparse()` tracks leading/trailing zero runs.

## Control Flow
Buffered mode appends to a global write buffer and flushes when full. Sparse mode scans each chunk for leading and trailing zeroes, accumulates seek distance, uses `lseek` or `do_punch_hole()` depending on preallocation position, writes only nonzero middle data, and delays trailing zero handling until later data or `sparse_end()`. Read-window mode aligns requested offsets to 1 KiB, reuses overlap from the prior window when possible, seeks if needed, reads missing bytes, and zero-fills the remainder if the source changes or read fails.

## State and Persistence Behavior
Writes destination files, may punch holes, seek over sparse ranges, truncate files, and allocate/free read/write buffers. Globals include `preallocated_len`, `sparse_seek`, `sparse_past_write`, and static write-buffer state. `map_struct->status` records the first read failure or `ENODATA`.

## Dependencies and Integration Points
Depends on syscall wrappers (`do_lseek`, `do_ftruncate`, `do_punch_hole`), sparse/preallocation feature macros from configure, transfer constants, logging, and cleanup. Used by receiver/sender match-transfer code for basis reads and destination writes.

## Risks and Test Signals
Risks include partial-write handling, stale global write-buffer state across files, sparse holes interacting with preallocated extents, incorrect offset accounting in `skip_matched()`, files changing during reads, and platform differences without `ftruncate`. Test signals include sparse and non-sparse transfers, in-place updates, preallocated sparse files, interrupted writes/reads, truncated source files during transfer, large aligned and unaligned map windows, and final `sparse_end()` file size checks.
