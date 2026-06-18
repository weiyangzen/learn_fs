# sources/test-tools/fio/lib/output_buffer.h

Purpose: declares `struct buf_output` and append/free helpers for dynamic output accumulation.

Important APIs/types: `struct buf_output { char *buf; size_t buflen; size_t max_buflen; }`, `buf_output_init`, `buf_output_free`, and `buf_output_add`.

Control flow/state: callers initialize before first use, append bytes, read `buf`/`buflen`, then free. The buffer can contain arbitrary bytes, not only C strings.

Dependencies/integration: includes `stddef.h`. Used by `log_buf` and JSON printing.

Risks/test signals: callers must not assume `buf` is non-null or NUL-terminated without checking length/capacity behavior. Tests should verify lifecycle and repeated append behavior.
