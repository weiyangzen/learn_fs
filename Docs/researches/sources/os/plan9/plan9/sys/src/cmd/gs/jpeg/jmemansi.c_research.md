# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemansi.c

Generic ANSI system-dependent memory manager backend. It assumes `malloc`, `free`, and `tmpfile()` are available.

It maps both small and large JPEG allocations to `malloc`/`free`, reports available memory as `cinfo->mem->max_memory_to_use - already_allocated`, and defaults the memory limit to `DEFAULT_MAX_MEM` or 1 MB.

Backing store uses an anonymous `tmpfile()`. The read/write methods seek with `fseek`, transfer with `JFREAD`/`JFWRITE`, and report JPEG temp-file errors through the IJG error manager. Closing the backing store just calls `fclose`, because `tmpfile()` handles deletion.
