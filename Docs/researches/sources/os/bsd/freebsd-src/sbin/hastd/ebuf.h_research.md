# File Research: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.h

`ebuf.h` declares the opaque extensible buffer API.

Key API:
- Allocate/free: `ebuf_alloc()`, `ebuf_free()`.
- Modify: `ebuf_add_head()`, `ebuf_add_tail()`, `ebuf_del_head()`, `ebuf_del_tail()`.
- Access: `ebuf_data()`, `ebuf_size()`.

The abstraction exposes only contiguous used data and hides head/tail capacity details.
