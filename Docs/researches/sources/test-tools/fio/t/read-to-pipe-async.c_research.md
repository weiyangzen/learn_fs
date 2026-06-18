# sources/test-tools/fio/t/read-to-pipe-async.c

Purpose: standalone latency experiment that reads a file in blocks and writes it to stdout while avoiding coordinated omission. If a read does not finish within a configured threshold, later reads can be issued by additional one-off threads so slow requests do not stop new submissions.

Important APIs and types: core structs are `stats`, `thread_data`, `writer_thread`, `reader_thread`, and `work_item`. Timing helpers include `utime_since()`, `add_lat()`, `plat_val_to_idx()`, `plat_idx_to_val()`, `calc_percentiles()`, and `show_latencies()`. Work scheduling is handled by `queue_work()`, `reader_fn()`, `reader_one_off()`, `reader_work()`, `writer_fn()`, `write_work()`, and `prune_done_entries()`.

Control flow: `main()` parses `-f`, `-b`, `-t`, and `-w`, opens and stats the input file, initializes reader and writer thread state, then loops over file blocks. For each block it allocates a `work_item`, queues it, waits up to `max_us` on the item's condition, and advances offsets regardless of whether the read completed. Finished reads are written in sequence by a separate writer thread by default. Shutdown waits for reader and writer completion, prints read/write latency percentiles and rates, and closes the file.

State and persistence: heap-allocated buffers and work items move through flists protected by pthread locks. Latency histograms use atomic increments. Output data is streamed to stdout; metrics and threshold violations go to stderr. No files are written by the program itself.

Dependencies and integration points: depends on pthreads, POSIX file APIs, fio internal `flist.h`, `log.h`, compiler helpers, and optional `CONFIG_PTHREAD_CONDATTR_SETCLOCK`. It is built as an auxiliary C tool rather than a Python harness.

Risks and test signals: inline writing is explicitly described as broken. There is careful sequence ordering for the separate writer, but memory cleanup depends on `prune_done_entries()` progress during loop and writer shutdown. The code assumes full writes to stdout and asserts otherwise. Signals are latency percentile output, over-threshold counts, read/write rates, and non-zero exits for option/open/stat failures.
