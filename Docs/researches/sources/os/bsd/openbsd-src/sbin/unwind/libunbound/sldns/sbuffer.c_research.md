# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/sbuffer.c

`sbuffer.c` implements the non-inline parts of the `sldns_buffer` memory-buffer API. `sldns_buffer_new()` allocates a dynamic buffer with position zero, limit equal to capacity, and clear status. `sldns_buffer_new_frm_data()` replaces an existing non-fixed buffer’s data with an allocated copy, while `sldns_buffer_init_frm_data()` wraps caller-owned data as a fixed, non-resizable buffer.

Capacity management is handled by `sldns_buffer_set_capacity()` and `sldns_buffer_reserve()`. Dynamic reserve grows capacity by 1.5x or to the exact required size, then resets the limit to capacity.

`sldns_buffer_printf()` writes formatted output at the current position if the status is OK, marking the buffer failed on `vsnprintf()` error. `sldns_buffer_free()` frees dynamic data and the buffer object, and `sldns_buffer_copy()` copies up to the destination capacity, silently truncating if needed, then flips the destination for reading.

The file is small because most typed read/write and position operations are inline in `sbuffer.h`.
