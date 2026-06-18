<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h

Purpose: This header declares the low-level FUSE session API, where handlers receive raw request headers and must explicitly send replies. It is the bridge between kernel protocol dispatch and filesystem-specific operations.

Important APIs and types: `fuse_entry_param` combines inode, generation, `struct stat`, and cache timeouts for entry replies. `fuse_lowlevel_ops` lists handler hooks for all supported opcodes, including newer operations such as `statx`, `syncfs`, `tmpfile`, `setupmapping`, `removemapping`, and `copy_file_range`. Reply functions cover errors, entries, creates, attrs, statx, readlink, open, write, copy_file_range_64, buffers, iovecs, statfs, xattr sizing, bmap, ioctl retry/final, and poll. Notification APIs invalidate inode/entry caches, delete dentries, poll, and retrieve kernel cached data.

Control flow and state: a session receives a buffer, dispatches by opcode to a `fuse_lowlevel_ops` function, and the handler owns the request until it calls a reply function or `fuse_reply_none`. Session APIs manage fd, buffer size, exit state, multithreaded loops, and user data.

Risks and test signals: request pointers other than `fuse_req_t` are only valid during the call unless copied. Missing replies can hang kernel requests; double replies can corrupt lifecycle. Tests should exercise delayed replies, interrupted requests returning `-ENOENT`, session exit/reset, notifications outside operation locks, and multithreaded receive/process loops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h -->
