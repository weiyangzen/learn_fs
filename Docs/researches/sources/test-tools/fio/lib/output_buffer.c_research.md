# sources/test-tools/fio/lib/output_buffer.c

Purpose: dynamic append-only byte buffer used by fio formatted output helpers.

Important APIs/functions: `buf_output_init`, `buf_output_free`, and `buf_output_add`.

Control flow: initialization zeroes capacity, length, and pointer. Add grows the buffer by at least 1024 bytes or the required deficit, zeroes part of the newly exposed region, copies the input bytes to the current end, and advances length. Free releases storage and resets the struct.

State/persistence: owns heap storage in `struct buf_output`; contents are not automatically NUL-terminated by length, though growth zeroing often leaves spare zero bytes after appended data.

Dependencies/integration: uses `minmax.h`. Consumed by JSON and logging functions for in-memory output assembly.

Risks/test signals: `realloc` failure is not checked before assigning `out->buf`, which can lose the old buffer and crash on subsequent `memset`/`memcpy`. Tests should cover growth, zero-length additions, large additions, and allocation-failure behavior under fault injection.
