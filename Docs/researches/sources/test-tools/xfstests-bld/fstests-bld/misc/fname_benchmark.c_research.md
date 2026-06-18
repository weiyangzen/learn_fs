# sources/test-tools/xfstests-bld/fstests-bld/misc/fname_benchmark.c

Purpose: `fname_benchmark.c` is a microbenchmark measuring CPU time spent creating, reading/looking up, and unlinking many files, optionally with file payloads and cache dropping.

Important APIs, types, and functions: operations `file_create()`, `file_read()`, `file_unlink()`; timing helpers `timeval_add()`, `timeval_sub()`, `upd_stat()`, `print_stat()`; `drop_cache()`; `main()` parsing `-b`, `-n`, `-r`, and `-d`. Global configuration includes `buf`, `bufsize`, and `time_stat` accumulators.

Control flow: `main()` parses buffer size, number of files, repeat count, and drop-cache flag. It optionally allocates a buffer, then for each repeat measures create loop for files named `f%04d`, optionally drops caches, measures read loop, optionally drops caches again, and measures unlink loop. At the end it prints configuration and accumulated user/system CPU times for create, lookup, unlink, and total process usage.

State and persistence: creates and deletes benchmark files in the current directory. If `-b` is used, writes/reads `bufsize` bytes from an allocated buffer. `drop_cache()` calls `sync()` and writes `"3\n"` to `/proc/sys/vm/drop_caches`.

Dependencies and integration points: built by `misc/Makefile.in` and called by `encrypt-fname-benchmark`. Depends on POSIX file APIs, `getrusage()`, and Linux `/proc/sys/vm/drop_caches` when cache dropping is enabled.

Risks: `drop_cache()` opens `/proc/sys/vm/drop_caches` with `O_RDONLY` but then writes to it; this appears wrong and should be `O_WRONLY`, so default `do_drop=1` may fail. Filenames use `f%04d`, but larger `num_files` still fit in the 256-byte buffer. Existing files with same names are truncated/deleted. Buffer contents are uninitialized, which is fine for throughput but can trip tools expecting deterministic data.

Test signals: run with `-d 0` in a scratch directory as non-root, then with cache dropping as root after fixing/validating open mode. Validate all created files are removed, option validation rejects invalid values, and timing output is sane.
