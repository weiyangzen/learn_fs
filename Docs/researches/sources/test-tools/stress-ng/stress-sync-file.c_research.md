# sources/test-tools/stress-ng/stress-sync-file.c

## Purpose
Implements the `sync-file` stressor, which exercises `sync_file_range()` over an allocated temporary file using forward, reverse, random, bad-file-descriptor, bad-offset, and open-ended range patterns. It targets filesystem writeback and Linux-specific sync-range behavior.

## Important APIs, Types, And Functions
`sync_modes[]` enumerates available mode combinations, including wait-before/write, wait-before/write/wait-after, write-only, wait-only, and no-op. `stress_sync_allocate()` truncates the file, `fdatasync()`s it, and `fallocate()`s the requested size. `stress_sync_file()` owns option handling, temp-file creation, sync loops, negative-input probes, and cleanup. The exported `stress_sync_file_info` classifies the stressor as I/O, filesystem, and OS, with `VERIFY_ALWAYS`.

## Control Flow
The stressor chooses total bytes from `sync-file-bytes`, maximize/minimize flags, and instance count, ensuring each worker has at least 1 MiB. It creates a temp directory and file, sets short write hints, probes pathconf async/sync I/O values, unlinks the pathname while keeping the file descriptor open, then waits at the sync barrier. Each loop chooses a random sync mode, reallocates the file, walks forward over random 1 KiB to roughly 128 KiB chunks calling `shim_sync_file_range()`, exercises invalid fd/offset/count and a half-file open-ended sync, reallocates again, walks reverse, reallocates again, and performs random aligned 128 KiB syncs. It increments bogo operations after the three main phases.

## State And Persistence
State is an open but unlinked temporary file descriptor and its allocated blocks. The filename is removed early, and the temp directory is removed at shutdown, so the filesystem should not retain named artifacts. Runtime state includes selected byte counts, sync mode, offsets, and return code. ENOSPC during allocation is treated as a recoverable loop condition.

## Dependencies And Integration Points
Requires `HAVE_SYNC_FILE_RANGE`; otherwise it exports an unimplemented stressor. It uses stress-ng filesystem temp helpers, write-hint helper, `shim_fallocate`, `shim_fdatasync`, `shim_sync_file_range`, pathconf probes, random numbers, sync barrier, option handling, and filesystem type reporting for diagnostics.

## Risks And Test Signals
`sync_file_range()` is Linux-specific and can return ENOSYS through the shim even when compiled. Filesystems may reject fallocate, run out of space, or expose unusual behavior for unlinked open files. Reverse mode passes `sync_file_bytes - offset`, so the first call starts one byte past the last valid offset for nonzero sizes; errors there would be surfaced as reverse sync failures. Test signals are clean skip on ENOSYS, continued operation across ENOSPC, no named temp-file residue, bogo progress, and absence of `pr_fail()` messages from forward/reverse/random sync phases.
