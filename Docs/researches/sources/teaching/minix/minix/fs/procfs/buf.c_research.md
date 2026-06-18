# File Research: sources/teaching/minix/minix/fs/procfs/buf.c

`buf.c` implements ProcFS's per-read output buffer abstraction. It stores static module state for the target buffer pointer, remaining writable bytes, used bytes, and a leading offset to skip for partial reads.

`buf_init` sets up a new output operation, capping output to `BUF_SIZE - 1` because formatted output needs room for a temporary trailing NUL. `buf_printf` appends formatted text with `vsnprintf`, still formatting skipped leading data because output size cannot be known in advance. It handles the skip window by moving unskipped data to the start once the offset is crossed, then clamps output to the requested length.

`buf_append` appends arbitrary bytes with the same skip/length accounting, used for binary-like command-line and environment output. `buf_result` returns the number of produced bytes, excluding any NUL terminator.
