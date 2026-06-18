<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp

Purpose: `fuse_conn_info_t` records negotiated protocol version and capability masks for a FUSE connection.

Important fields: `proto_major` and `proto_minor` identify the negotiated kernel protocol; `capable` contains features advertised by the kernel/runtime, and `want` contains features requested by the filesystem.

State and integration: a pointer is passed to init callbacks in both high-level and low-level APIs. The same data is embedded in `fuse_req_t`, letting request handling know what features are active.

Risks and test signals: feature bits must stay aligned with `fuse_common.h` and `fuse_kernel.h`. Init negotiation tests should verify capabilities such as writeback cache, max pages, passthrough, and request timeout are reflected correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp -->
