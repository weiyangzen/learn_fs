# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fseeko.c

Read completely: 276 lines.

This file implements `fseeko`, the main stdio seek engine. It validates seekability and offsets, converts `SEEK_CUR` into absolute positions accounting for buffered read/write and ungetc data, attempts optimized seeks within or near the current read buffer for regular files, and falls back to flushing plus calling the stream seek hook.

Important interactions: used by `fseek`, `fsetpos`, and code that needs large offsets.

Security/reliability notes: clears EOF and discards ungetc data on successful seek. Optimization is disabled for write, read-write, unbuffered, or non-regular streams.
