# File Research: sources/os/bsd/freebsd-src/sbin/hastd/ebuf.c

`ebuf.c` implements an extensible byte buffer that can grow at both the head and tail.

Key behavior:
- `ebuf_alloc()` allocates a buffer with initial headroom, placing used data at one quarter of a page into the allocation.
- `ebuf_add_head()` prepends data or reserves head space, extending the head when needed.
- `ebuf_add_tail()` appends data or reserves tail space, extending the tail when needed.
- `ebuf_del_head()` and `ebuf_del_tail()` remove bytes from either side.
- `ebuf_data()` returns the contiguous used-data pointer and optional size.
- `ebuf_size()` returns used size.
- Head extension allocates a new buffer and copies used data.
- Tail extension uses `realloc()` and adjusts pointers.

Important details:
- Used by the HAST protocol layer to prepend the fixed main header before serialized nv data.
- Internal magic value assertions catch invalid use in debug/asserting builds.
- `ebuf_head_extend()` currently does not free the old allocation after copying, which is notable when reviewing memory behavior.
