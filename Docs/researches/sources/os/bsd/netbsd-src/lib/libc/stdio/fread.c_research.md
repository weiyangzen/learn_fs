# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fread.c

Read completely: 141 lines.

This file implements `fread`. It detects `size * count` overflow, returns zero for zero-sized reads, locks the stream, handles unbuffered streams by reading directly into the caller buffer, otherwise drains internal buffers and refills with `__srefill`.

Important interactions: core buffered input path for binary reads.

Security/reliability notes: overflow sets `EOVERFLOW` and stream error. Partial reads return complete item count only.
