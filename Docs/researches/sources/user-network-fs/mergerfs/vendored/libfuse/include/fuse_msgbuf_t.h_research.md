<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h

Purpose: `fuse_msgbuf_t` is the simple C struct backing message buffers: a 32-bit size and a `char*` memory pointer.

Important behavior: the struct separates metadata from allocated payload memory. It does not encode ownership policy; allocation/free routines in `fuse_msgbuf.hpp` own that contract.

State and integration: instances are passed through receive and processing code to hold raw FUSE messages.

Risks and test signals: size is `uint32_t`, so callers must avoid truncating larger negotiated sizes. Tests should validate allocation sizes, null handling, and max request boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h -->
