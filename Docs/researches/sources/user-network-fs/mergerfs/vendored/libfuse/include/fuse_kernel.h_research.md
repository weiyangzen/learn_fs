<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h

Purpose: This is the kernel/userspace FUSE protocol ABI header, updated through protocol minor 45. It defines version constants, opcodes, notify codes, feature flags, request/reply structs, dirent alignment macros, passthrough ioctls, DAX mapping structs, statx structs, io_uring structs, and request-timeout support.

Important APIs and types: core structs include `fuse_in_header`, `fuse_out_header`, `fuse_attr`, `fuse_entry_out`, `fuse_attr_out`, `fuse_open_in/out`, read/write, xattr, lock, ioctl, poll, init, statx, copy-file-range, setup/removemapping, and notification payloads. Macros such as `FUSE_REC_ALIGN`, `FUSE_DIRENT_SIZE`, and `FUSE_DIRENTPLUS_SIZE` define exact buffer layout. Capability flags span both low 32-bit `flags` and high `flags2` bits.

Control flow and state: the kernel sends a `fuse_in_header` plus opcode-specific payload, userspace replies with `fuse_out_header` plus output payload, and init negotiation chooses protocol/features. No state is stored in the header, but every field is an ABI contract for persistent kernel connection state such as lookup counts, file handles, backing IDs, cache timeout, and mapping windows.

Risks and test signals: this file is highly ABI-sensitive; field-size, padding, endian, or flag drift can make the filesystem unusable. Some macros reference platform constants such as `PAGE_SIZE`. Tests should include compile-time size/offset checks against Linux headers, init negotiation for flags2 features, readdir alignment validation, and exercised opcodes for newer features like statx, passthrough, request timeout, and copy_file_range_64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h -->
