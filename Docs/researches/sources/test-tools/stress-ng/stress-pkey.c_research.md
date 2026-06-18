# sources/test-tools/stress-ng/stress-pkey.c

Purpose: `stress-pkey.c` implements the `pkey` stressor, exercising memory protection key allocation, free, get/set, and `pkey_mprotect` permission changes on a small anonymous mapping.

Important APIs/types/functions: the build requires `HAVE_PKEY_MPROTECT`. `stress_pkey()` maps eight pages, randomly chooses one page per iteration, uses shim wrappers `shim_pkey_alloc()`, `shim_pkey_free()`, `shim_pkey_mprotect()`, `shim_pkey_get()`, and `shim_pkey_set()`, and drives valid and invalid pkey paths.

Control flow: after mmap and sync, each loop exercises invalid allocation flags and rights, invalid frees, tries to allocate a pkey with `PKEY_DISABLE_WRITE` or no rights, falls back to pkey `-1` if allocation fails, applies `PROT_NONE`, read, write, read/write, exec, and combined exec permissions via `pkey_mprotect`, then tests invalid protection flags, unaligned address, address wrap, and zero length. If a real pkey was allocated, it gets and restores rights and frees it.

State and persistence behavior: state is the anonymous eight-page mapping and transient pkey allocations. No files are created. Protection changes are reset by later `pkey_mprotect` calls or by unmapping at deinit.

Dependencies and integration points: Linux/glibc pkey syscall support via shims, mmap helpers, stress-ng sync/state helpers, random page selection, and `CLASS_OS` registration.

Risks: pkey availability depends on CPU, kernel, and libc; ENOSYS during `pkey_mprotect` converts to not-implemented. Using pkey `-1` intentionally falls back toward standard mprotect semantics. Some architectures may reject exec/write combinations differently.

Test signals: direct `--pkey` should bogo-progress or skip as not implemented. Useful checks include pkey exhaustion, ENOSYS fallback, invalid argument tolerance, and that mappings are unmapped after failure and success paths.
