# sources/test-tools/stress-ng/stress-metamix.c

Purpose: `stress-metamix.c` implements the `metamix` filesystem stressor, modeled after Lucene-like metadata and random access patterns. It creates files with many small writes at varying offsets, syncs and stats them, reads them back in checksum-derived order, optionally verifies checksums, and mmap-checks page-aligned extents.

Important APIs/types/functions: `file_info_t` records offset, data length, checksum, and validity for up to `METAMIX_WRITES` writes. `stress_metamix_cmp` sorts entries by checksum to randomize later read order. `stress_metamix_file` performs one complete file lifecycle. `counter_lock` coordinates bogo operation accounting across the parent and `METAMIX_PROCS` forked helper processes.

Control flow: `stress_metamix` installs SIGCHLD handling, mmaps a shared PID list, creates the counter lock, computes per-instance bytes, creates the temp directory, records filesystem type text for diagnostics, then forks 15 children. Each child waits for synchronized start and repeatedly calls `stress_metamix_file` while `stress_bogo_inc_lock` permits. The parent also runs the file workload, then reaps children with SIGALRM and cleans the temp directory, lock, and PID mapping.

State and persistence behavior: persistent state is intentionally temporary: one temp directory per stressor instance and per-iteration temp files that are unlinked at the end of `stress_metamix_file`. Checksums live only in stack `file_info`. `counter_lock` is a stress-ng shared lock; PID coordination is in an mmaped shared `stress_pid_t` array.

Dependencies and integration points: the file uses stress-ng filesystem temp helpers, hash helpers, mmap helpers, sort wrappers, process synchronization, kill/wait helpers, and scheduler application in children. It registers `stress_metamix_info` as `CLASS_FILESYSTEM | CLASS_OS` with optional verification and an `--metamix-bytes` option.

Risks: the write-size calculation casts `max_seek` through `uint8_t` for `stress_mwc8modn`, so very small `metamix_bytes` must stay above the enforced minimum. Partial writes break out and can leave fewer valid entries than `METAMIX_WRITES`, which later code handles through `n`. Filesystem behavior varies for `fdatasync`, `fsync` on directories, sparse regions, and mmap of holes. Any cleanup regression can leave temp files behind or orphan helper processes.

Test signals: run `stress-ng --metamix 1 --metamix-ops 1 --verify`, run on tmpfs and a disk filesystem, test small `--metamix-bytes 512`, and confirm no temp files remain. Verification should catch checksum or file-size mismatches; non-verify mode should still exercise stat/lstat, fdatasync, fsync, random reads, mmap reads, and unlink cleanup.
