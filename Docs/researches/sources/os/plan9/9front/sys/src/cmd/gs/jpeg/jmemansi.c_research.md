# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemansi.c

Purpose: generic ANSI system-dependent memory-manager backend.

Important behavior:
- Assumes `malloc`, `free`, and `tmpfile()` are available.
- Maps both small and large JPEG allocations to `malloc`/`free`.
- Reports available memory as `cinfo->mem->max_memory_to_use - already_allocated`.
- Defaults the memory limit to `DEFAULT_MAX_MEM`, or 1 MB if not overridden.

Backing store:
- Uses anonymous `tmpfile()`.
- Read/write methods seek with `fseek`, transfer with `JFREAD`/`JFWRITE`, and report temp-file errors through IJG error macros.
- Closing backing store calls `fclose`; `tmpfile()` handles deletion.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`.
