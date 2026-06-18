# File Research: sources/teaching/xv6-public/pipe.c

Implements kernel pipes.

Key behavior:
- `pipealloc` allocates two file objects and one page-backed pipe, configuring read and write ends.
- `pipeclose` marks an end closed, wakes the opposite side, and frees the pipe when both ends close.
- `pipewrite` writes byte-by-byte into a circular 512-byte buffer, sleeping when full and failing if reader closed or process killed.
- `piperead` sleeps while empty and writer open, then copies available bytes and wakes writers.

Important interactions:
- Uses `sleep`/`wakeup` on `nread` and `nwrite`.
- Pipe memory comes from `kalloc`.
