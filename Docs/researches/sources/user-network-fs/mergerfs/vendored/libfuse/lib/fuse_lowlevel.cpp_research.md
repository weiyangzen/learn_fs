# sources/user-network-fs/mergerfs/vendored/libfuse/lib/fuse_lowlevel.cpp

## Purpose
`fuse_lowlevel.cpp` is the kernel protocol layer. It reads raw FUSE messages, allocates request objects, dispatches opcodes to low-level handlers, performs the FUSE INIT negotiation, marshals all replies, and sends kernel notify messages.

## Important APIs, Types, and Functions
`struct fuse_ll` stores low-level ops, owner uid, negotiated `fuse_conn_info_t`, mutex, init/destroy flags, and pending notify list. Reply APIs include `fuse_reply_err`, `fuse_reply_none`, `fuse_reply_entry`, `fuse_reply_create`, `fuse_reply_attr`, `fuse_reply_statx`, `fuse_reply_open`, `fuse_reply_write`, `fuse_reply_buf`, `fuse_reply_data`, `fuse_reply_statfs`, `fuse_reply_xattr`, `fuse_reply_ioctl`, and `fuse_reply_poll`. Notify APIs include poll, invalidate inode/entry, delete, and retrieve. `fuse_lowlevel_new_common` creates the session.

## Control Flow
Before INIT, the session process callback is `fuse_ll_buf_process_read_init`, which rejects non-INIT messages. `do_init` parses kernel capabilities, calls the high-level init callback, intersects requested capabilities with supported ones, configures max pages/write size/background limits, updates message-buffer size, and replies with the ABI-specific init struct size. After INIT, `fuse_ll_buf_process_read` builds a `fuse_req_t`, copies header context, validates the opcode against `fuse_ll_funcs`, and invokes the mapped operation. Reply helpers write a `fuse_out_header` plus payload through `writev` and free the request.

## State and Persistence
Negotiated connection state persists for the process lifetime. Pending notification requests are kept in an intrusive list until the kernel replies. There is no durable storage. Request objects are pooled by `fuse_req.cpp`; message buffers are managed by the loop.

## Dependencies and Integration Points
This file depends on kernel ABI structs from `fuse_kernel.h`, request/session internals from `fuse_i.hpp`, pooled message/request allocation, debug/syslog helpers, `fuse_cfg`, and POSIX `read`/`writev`.

## Risks
The FUSE ABI is size- and version-sensitive; wrong compatibility sizes or capability flags can break mounts. Every reply path must free the request exactly once. `fuse_send_msg` assumes full `writev` success and does not retry partial writes. Notify unique ids and list operations require correct locking.

## Test Signals
Test INIT with old/new minor versions, capability negotiation, max_pages resizing, unsupported opcode ENOSYS, short read EIO, debug logging, every reply helper's payload size, ioctl retry on 32-bit compat paths, notify poll/inval/delete/retrieve, and destroy called exactly once.
