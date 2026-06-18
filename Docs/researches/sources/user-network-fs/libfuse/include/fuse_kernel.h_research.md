# sources/user-network-fs/libfuse/include/fuse_kernel.h

`fuse_kernel.h` is the userspace copy of the FUSE kernel wire ABI. It defines protocol version 7.45, request/reply opcodes, capability and init flags, notify codes, ioctl constants, and packed request/reply structures exchanged over `/dev/fuse`, CUSE, and io-uring transport paths.

There are no functions. Core wire types include `fuse_attr`, `fuse_statx`, `fuse_kstatfs`, `fuse_file_lock`, request/reply payloads for namespace, attributes, I/O, locking, xattrs, init, CUSE, ioctl, poll, fallocate, lseek, copy-file-range, DAX mappings, security-context extensions, supplementary groups, notifications, passthrough backing maps, and `fuse_uring_*` structures. Enumerations include `fuse_opcode`, `fuse_notify_code`, `fuse_ext_type`, and `fuse_uring_cmd`.

Control flow is protocol-level: the kernel sends `FUSE_INIT`, userspace replies with compatible versions/flags, later requests use `fuse_in_header` plus opcode payloads, replies use `fuse_out_header`, and notifications reverse direction for invalidation, store/retrieve, pruning, resend, poll, and epoch events. State crossing the ABI includes inode ids, lookup counts, file handles, lock owners, cache timeouts, caller context, security contexts, supplementary groups, DAX mappings, backing ids, and unique request ids.

Risks are ABI drift from kernel UAPI, padding/size/endian mismatches, incorrect `flags2` handling for bits above 31, resend/idmap/security-context/io-uring edge cases, and directory record alignment. Test signals include size/offset checks, negotiation downgrade tests, serialization coverage by opcode, directory alignment, CUSE init, passthrough ioctl, security context parsing, idmap sentinels, and io-uring layout checks.
