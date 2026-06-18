# File Research: sources/os/plan9/plan9/sys/src/9/omap/uncached.h

Header-level allocator macro override for forcing USB/EHCI data structures into uncached memory.

Key contents:
- Documents spurious EHCI transaction errors when cached write-back memory is used for USB data.
- Redefines memory/block allocation/free names:
  - `free` to `ucfree`
  - `malloc`/`smalloc` to `myucalloc`
  - `mallocz` to `ucallocz`
  - `xspanalloc` to `ucallocalign`
  - block alloc/free functions to uncached equivalents.
- Implements `ucallocz()` and `myucalloc()` wrappers.

Role:
- Intended to be included before USB/EHCI code that assumes normal allocator names, redirecting allocations to uncached memory.

Notable risks:
- Macro substitution is broad and can surprise included code.
- `ucallocz` ignores its second argument and always zeroes.
- Allocation failure panics rather than returning nil.
