# sources/test-tools/stress-ng/stress-pseek.c research

Purpose: implements `pseek`, a mixed process/thread filesystem stressor that writes and reads deterministic data at fixed or random offsets using both `lseek`+`read/write` and positional `pread/pwrite`.

Important APIs, types, and functions: shared `stress_peekio_info_t` stores the file descriptor, filesystem type, I/O size, randomization flag, and parent PID. `stress_peekio_proc_t` records each child or pthread worker's buffer, I/O mode, process identity, return code, and throughput counters. `data_value()` and `pseek_fill_buf()` generate offset/proc-specific data. `stress_pseek_write_offset()` and `stress_pseek_read_offset()` perform and verify I/O.

Control flow: `stress_pseek()` allocates a shared process table, clamps `pseek-io-size`, maps per-worker buffers, creates and unlinks a temp file, truncates it to the chunked working size, synchronizes, then starts workers 1..N-1 as alternating pthreads and forked children while worker 0 runs inline. Each worker loops write/read/yield over its assigned chunk until stopped or failure signals the parent. Cleanup kills/cancels workers, aggregates rates, closes/unlinks/removes temp storage, and unmaps buffers.

State and persistence: transient temp directory/file is unlinked after open, and anonymous mappings hold process tables and buffers. No persistent data should survive successful cleanup.

Dependencies and integration: uses stress-ng temp-file helpers, mmap, pthreads when available, fork/wait helpers, scheduler yield, metrics, and option handling. It registers as `CLASS_IO | CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: shared file offset mode is deliberately non-atomic and therefore not data-verified on reads; only positional mode verifies. ENOSPC is treated as graceful stop, but partial reads/writes are failures. Mixed process/thread access to a shared descriptor stresses kernel offset locking and filesystem behavior.

Test signals: write/read MB/sec metrics, data mismatch failures in positional mode, ENOSPC early exit, child/pthread return codes, and temp-dir cleanup are key signals.
