# sources/test-tools/fio/t/dedupe.c

## Purpose
Scans a file or block device for duplicate fixed-size extents and reports dedupe ratio, fio-compatible `dedupe_percentage`, and optionally compressed unique capacity or full duplicate extent lists.

## Important APIs, Types, and Functions
`struct worker_thread` tracks per-thread progress, duplicate counts, zlib state, and file descriptor. `struct chunk` stores a unique MD5 hash in a fio red-black tree; `struct extent` records offsets when collision checking or dumps are enabled. `get_size()`, `get_work()`, `read_blocks()`, `crc_buf()`, `insert_chunk()`, `insert_chunks()`, `thread_fn()`, `run_dedupe_threads()`, `dedupe_check()`, `iter_rb_tree()`, and `show_stat()` form the scan pipeline.

## Control Flow
`main()` parses block size, threads, direct I/O, bloom, collision, progress, dump, and compression options, initializes fio architecture/runtime state, then scans the input. `dedupe_check()` opens the target and computes an aligned size. Worker threads claim `chunk_size` ranges under `size_lock`, read them, hash every `blocksize` block, and either insert hashes into a shared red-black tree or update a probabilistic bloom filter under `rb_lock`. After joining, the main thread derives totals and prints ratio/statistics.

## State and Persistence Behavior
The target is read-only. Persistent behavior is stdout/stderr output only. Shared in-memory state includes `cur_offset`, `total_size`, `rb_root`, optional `bloom`, global `file`, semaphore locks, and per-thread zlib buffers. When compression is enabled, unique blocks are reread and deflated to estimate capacity.

## Dependencies and Integration Points
Uses fio internals for file/device sizing, semaphores, aligned memory, red-black trees, bloom filters, MD5, timing, architecture setup, cleanup, and logging. Uses zlib for compression estimates and pthreads for parallel scanning.

## Risks
Default bloom mode is approximate and cannot support exact duplicate counts, dumps, collision checks, or compression. The progress loop stops when any thread is done rather than all threads, so display can end early. `thread_fn()` marks normal no-work termination as `err = 1`, though the joined error is not aggregated. `blocksize` should be power-of-two-like because size alignment masks with `blocksize - 1`. Large exact scans can consume significant memory for unique chunks and extents.

## Test Signals
Good coverage would compare known-pattern files against expected duplicate percentages, exercise bloom versus exact tree modes, verify collision-check rejection of MD5 collisions by content, confirm `O_DIRECT` alignment behavior, and validate compression output for repeated and random data.
