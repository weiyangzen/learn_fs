# sources/security-integrity/audit-userspace/auparse/data_buf.c

Purpose: Implements the `DataBuf` helper used by auparse to store and consume buffer/feed input with efficient append, advance, optional head preservation, and reset behavior.

Important APIs, types, and functions: Implements `databuf_print()`, `databuf_init()`, `databuf_free()`, `databuf_append()`, `databuf_replace()`, `databuf_advance()`, and `databuf_reset()`. Internal helpers include `databuf_end()`, `databuf_tail_size()`, `databuf_tail_available()`, and `databuf_shift_data_to_beginning()`.

Control flow: `databuf_init()` zeroes state and optionally allocates an initial buffer. `databuf_append()` ignores NULL/zero input, shifts data to the start when allowed and tail space is insufficient, grows allocation by doubling or required size, copies new bytes to the end, updates length and `max_len`, and returns status. `databuf_replace()` clears length then appends. `databuf_advance()` moves the logical beginning forward by up to available length and returns `ESPIPE` if asked to advance too far. `databuf_reset()` only works with `DATABUF_FLAG_PRESERVE_HEAD`, restoring offset to zero and length to the maximum length previously seen.

State and persistence: `DataBuf` owns heap memory via `alloc_ptr`, tracks allocated size, logical offset/length, maximum length, and flags. No persistence beyond the owning parser state.

Dependencies and integration points: Used by `auparse.c` for `AUSOURCE_BUFFER`, `AUSOURCE_BUFFER_ARRAY`, and `AUSOURCE_FEED`. It depends only on libc and `data_buf.h`.

Risks and edge cases: `databuf_append()` uses `memmove(databuf_end(db), src, src_size)`, which handles overlap but relies on correct logical bounds. `databuf_reset()` reconstructs preserved buffers by `max_len`, so callers using preserve-head must ensure `max_len` reflects the intended original input. Integer overflow is partially handled by required-size comparisons but not with explicit `SIZE_MAX` guards for all additions. `databuf_print()` writes to stdout and is diagnostic-only.

Test signals: There is an optional `#ifdef TEST` harness in the file, but normal coverage is indirect through auparse buffer/feed tests.
