# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemname.c

Generic system-dependent memory backend for platforms where temporary files must be explicitly named. It is similar to `jmemansi.c` but uses `fopen` on generated filenames instead of `tmpfile()`.

Small and large allocations use `malloc/free`, and available memory is computed from `max_memory_to_use - already_allocated`. The default max memory is 1 MB.

Temporary names are built under `TEMP_DIRECTORY`, defaulting to `/usr/tmp/`. With `mktemp()` available, filenames use a trailing `XXXXXX` template; with `NO_MKTEMP`, the code increments a numeric suffix and probes for non-existing files. Backing store reads and writes use `fseek` plus `JFREAD`/`JFWRITE`; close calls `fclose` and `unlink`.
