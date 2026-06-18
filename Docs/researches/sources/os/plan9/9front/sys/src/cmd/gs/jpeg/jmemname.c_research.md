# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemname.c

Purpose: generic system-dependent memory backend for platforms where temporary files must be explicitly named.

Important behavior:
- Similar to `jmemansi.c`, but uses `fopen()` on generated filenames instead of `tmpfile()`.
- Small and large allocations use `malloc/free`.
- Available memory is computed from `max_memory_to_use - already_allocated`.
- Default max memory is 1 MB.

Temporary-file naming:
- Uses `TEMP_DIRECTORY`, defaulting to `/usr/tmp/`.
- With `mktemp()` available, filenames use a trailing `XXXXXX` template.
- With `NO_MKTEMP`, the code increments a numeric suffix and probes for a non-existing file.

Backing store:
- Reads and writes use `fseek` plus `JFREAD`/`JFWRITE`.
- Close calls `fclose` and `unlink`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`.
