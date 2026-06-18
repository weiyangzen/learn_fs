# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mmapobj.h

Purpose: Declares kernel-side mmap object helpers.

Key definitions:
- `LIBVA_CACHED_SEGS` is 3, the number of `mmapobj_result_t` entries expected to be stack-cached for common ELF objects.

Key APIs:
- Kernel-only `mmapobj_unmap()`.
- Kernel-internal `mmapobj(vnode_t *, uint_t, mmapobj_result_t *, uint_t *, size_t, cred_t *)`.

Important detail: This header expects `mmapobj_result_t` from `sys/mman.h` and uses vnode/credential types, tying object mapping directly to VFS objects.

Relevance to subset A: Directly relevant to VFS-backed executable/object mapping.
