# File Research: sources/teaching/xv6-riscv/kernel/pipe.c

Implements anonymous pipes as kernel-resident circular buffers exposed through `struct file`.

Important behavior:
- `pipealloc()` allocates two file objects and one page-backed `struct pipe`.
- `pipeclose()` marks read/write ends closed, wakes opposite waiters, and frees the pipe when both ends close.
- `pipewrite()` copies bytes from user memory, sleeps when full, and fails if no reader or process killed.
- `piperead()` sleeps while empty and writer open, copies bytes to user memory, and wakes writers.

Filesystem relevance: pipes share the file descriptor layer with inode and device files. `file.c` dispatches `FD_PIPE` reads/writes here.
