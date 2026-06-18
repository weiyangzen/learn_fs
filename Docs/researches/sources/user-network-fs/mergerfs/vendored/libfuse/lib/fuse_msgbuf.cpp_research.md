# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_msgbuf.cpp

## Purpose
`fuse_msgbuf.cpp` manages page-aligned buffers used to read requests from `/dev/fuse` and reply with page-aligned data.

## Important APIs, Types, and Functions
Exports include `msgbuf_alloc`, `msgbuf_alloc_page_aligned`, `msgbuf_free`, `msgbuf_get_bufsize`, `msgbuf_get_pagesize`, `msgbuf_set_bufsize`, `msgbuf_alloc_count`, `msgbuf_gc`, and `msgbuf_clear`. `PageAlignedAllocator` uses `posix_memalign`; `ShouldPoolMsgbuf` keeps only buffers matching current size.

## Control Flow
A constructor queries system page size, asserts the write-header alignment fits within a page, and initializes the default buffer size. Allocations come from an `ObjPool` sized to `g_bufsize`. `msgbuf_alloc` returns a buffer whose `mem` pointer is offset so `fuse_in_header` and `fuse_write_in` can be prepended/aligned for write requests. `msgbuf_alloc_page_aligned` returns a page-aligned data region. Changing max pages updates `g_bufsize` and clears the pool.

## State and Persistence
Global page size, buffer size, and object pool state persist for the process. Buffers are not durable and are recycled until GC/clear or size changes.

## Dependencies and Integration Points
The file depends on `fuse_kernel.h`, `fuse_msgbuf.hpp`, `objpool.hpp`, `fatal.hpp`, and POSIX memory/page APIs. It is used by `fuse_loop.cpp` for request reads and by `fuse.cpp` for read replies.

## Risks
`g_bufsize` is global and pool clearing during active use would be unsafe if called outside init/maintenance expectations. Alignment assumptions are critical for kernel read/write layout. Allocation failure must propagate to avoid null dereferences.

## Test Signals
Verify page size discovery, default and negotiated max-page sizes, write-aligned and page-aligned pointer offsets, pool reuse count, pool clearing after size changes, and ENOMEM handling in read paths.
