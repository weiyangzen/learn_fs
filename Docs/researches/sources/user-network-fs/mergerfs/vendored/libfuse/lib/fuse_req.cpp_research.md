# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_req.cpp

## Purpose
`fuse_req.cpp` provides pooled allocation for low-level request objects.

## Important APIs, Types, and Functions
The file exports `fuse_req_alloc()` and `fuse_req_free(fuse_req_t*)`, backed by a static `ObjPool<fuse_req_t> g_pool`.

## Control Flow
`fuse_lowlevel.cpp` calls `fuse_req_alloc` after reading a kernel request and fills the returned structure with context, connection, session, fd, and ioctl state. Reply helpers call `fuse_req_free` after writing the response, while no-reply operations such as forget call `fuse_reply_none`, which also frees the request.

## State and Persistence
The object pool is process-local and persists for the lifetime of the library. Requests are transient and must not escape after a reply. There is no persistent storage.

## Dependencies and Integration Points
It includes `fuse_req.hpp` and `objpool.hpp`. Its correctness is tightly coupled to reply ownership in `fuse_lowlevel.cpp` and every `fuse_lib_*` handler that must produce exactly one reply or no-reply free.

## Risks
Leaks occur if a handler returns without replying. Double frees occur if a handler replies twice or calls `fuse_req_free` after a reply helper. Thread safety depends on `ObjPool` behavior under the read/process thread model.

## Test Signals
Use request storm tests, unsupported opcode paths, forget/no-reply paths, ENOMEM allocation failure, and sanitizers to catch leaks or double frees around interrupted open/create replies.
