# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup.h

Generic cleanup-attribute helper header.

Macros/functions:
- `__cleanup(fn)` wraps `__attribute__((cleanup(fn)))`.
- `DECLARE_CLEANUP_FUNC` and `DEFINE_CLEANUP_FUNC` create typed cleanup wrappers.
- `freep()` backs `__cleanup_free` for normal `free`.
- `libnvme_freep()` backs `__cleanup_libnvme_free` for memory allocated with `libnvme_alloc`.

Dependencies:
- Includes `<stdlib.h>` and `<nvme/mem.h>`.

Integration:
- Used across crypto, fabrics, ioctl, and discovery paths for structured cleanup on error returns.
- Helps keep complex functions from accumulating manual unwind labels.

Risks:
- Compiler-specific feature; portability depends on supported toolchain.
- Ownership transfer must explicitly NULL out cleanup-managed pointers, as seen in code that assigns output pointers after allocation.
