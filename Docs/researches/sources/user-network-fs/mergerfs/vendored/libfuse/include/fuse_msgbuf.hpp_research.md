<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp

Purpose: This header declares allocation and garbage-collection functions for FUSE message buffers. It abstracts page size, configured buffer size, and allocation pooling for `fuse_msgbuf_t`.

Important APIs: `msgbuf_get_pagesize`, `msgbuf_set_bufsize`, and `msgbuf_get_bufsize` expose buffer sizing. `msgbuf_alloc` and `msgbuf_alloc_page_aligned` allocate message buffers; `msgbuf_free` returns them; `msgbuf_clear`, `msgbuf_gc`, and `msgbuf_alloc_count` manage or inspect the backing pool.

State and integration: implementation state is outside this header, likely a global object pool/cache. The buffers are used by receive/process loops to hold raw FUSE kernel messages.

Risks and test signals: buffer size must be large enough for negotiated max write/pages, and page-aligned buffers must really satisfy kernel/direct I/O expectations. Tests should cover allocation/free counts, GC, page alignment, buffer resizing before and after allocations, and large request handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp -->
