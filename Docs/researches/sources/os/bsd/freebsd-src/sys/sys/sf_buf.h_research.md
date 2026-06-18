# File Research: sources/os/bsd/freebsd-src/sys/sys/sf_buf.h

Sendfile buffer and temporary physical-page mapping interface.

Key responsibilities:
- Defines `struct sfstat` counters for `sendfile(2)` behavior and sf_buf allocation failures/waits.
- Documents architecture-dependent sf_buf modes: `SFBUF`, `SFBUF_CPUSET`, `SFBUF_NOMD`, `SFBUF_MAP`, and `SFBUF_PROCESS_PAGE`.
- Defines `struct sf_buf` for platforms requiring a mapping hash, including page, KVA, reference count, and optional CPU mask.
- Declares or inlines `sf_buf_alloc()`, `sf_buf_free()`, `sf_buf_ref()`, `sf_buf_kva()`, `sf_buf_page()`, `sf_buf_map()`, and `sf_buf_unmap()`.
- Defines allocation flags `SFB_CATCH`, `SFB_CPUPRIVATE`, `SFB_NOWAIT`, and `SFB_DEFAULT`.

Important patterns:
- On platforms with a direct map, an `sf_buf *` can be represented by the `vm_page_t` itself.
- On platforms without universal direct mapping, sf_bufs provide transient kernel virtual mappings for pages.
- Statistics are exposed through a `counter_u64_t` array indexed by `struct sfstat` field offset.

Research relevance:
- Important VM/network/filesystem bridge for zero-copy or low-copy file transmission.
- Shows how FreeBSD abstracts page mapping costs across 32-bit and 64-bit architectures.
