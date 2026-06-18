<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp

Purpose: This header declares the libfuse debug and syslog tracing API implemented in `lib/debug.cpp`. It is the integration surface for printing decoded FUSE protocol input and output records.

Important APIs: `fuse_debug_set_output` chooses stderr or an append-mode file. The `fuse_debug_*_out` functions format specific reply payloads such as open, init, entry, attr, write, statfs, xattr, lock, bmap, statx, data, ioctl, and poll. `fuse_debug_in_header` and `fuse_debug_out_header` decode generic kernel request and reply headers. `fuse_debug_init_flag_name` converts capability bits to names; syslog helpers summarize init negotiation.

State and integration: the declarations depend on `fuse_kernel.h` structs and route output through the global `fuse_cfg` log sink. They are called from request processing and reply paths to provide line-oriented diagnostics.

Risks and test signals: tracing must stay ABI-synchronized with `fuse_kernel.h`; missing new opcodes or flags silently reduce observability. Tests should enable debug output, exercise representative opcodes, and verify logs are line-complete under concurrent calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp -->
