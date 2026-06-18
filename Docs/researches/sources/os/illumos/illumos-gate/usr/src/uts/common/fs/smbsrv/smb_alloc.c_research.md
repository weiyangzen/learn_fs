# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_alloc.c

Implements SMB memory allocation wrappers and request-scoped temporary storage.

Key behavior:
- Adds an internal header before every allocation with magic, size, owning request pointer, and list node.
- Provides global allocation/free/reallocation APIs with optional zeroing.
- Provides request-scoped `smb_srm_*` APIs that automatically link allocations into `sr->sr_storage`.
- `smb_srm_fini()` frees all request-scoped allocations and destroys the storage list.
- Reallocation returns original pointer when shrinking, optionally zeroes truncated bytes, and allocates/copies/frees when growing.

Important dependencies:
- Kernel memory allocator: `kmem_alloc`, `kmem_zalloc`, `kmem_free`.
- illumos list API.

Notable details:
- `smb_free()` asserts the caller-provided request matches the allocation owner.
- Header magic catches invalid frees in debug/assert builds.
