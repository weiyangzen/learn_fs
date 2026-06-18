# sources/sync-backup/unison/dev/test-limits.c

Purpose: tiny C helper for probing process memory limits by allocating memory until `malloc` fails.

Important API: `main` loops up to 4 GiB in 4 KiB chunks, writes the first int of each allocation to force a touched page, intentionally discards the pointer, and prints allocated KiB.

Control flow: allocation continues until failure or the fixed 4 GiB ceiling is reached. There is no cleanup because the process exits immediately after printing.

State/persistence: no files; it consumes address space and memory pages during the process lifetime.

Dependencies/integration: standard C library only. Intended to be compiled and run under different `ulimit`/`setrlimit` settings.

Risks: intentionally leaks every successful allocation. The hard cap prevents unbounded growth if limits are ineffective, but running it can still stress memory. It measures rough allocation behavior, not Unison-specific memory use.

Test signals: stdout numeric KiB value indicates observed allocation ceiling.
