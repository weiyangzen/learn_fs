# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dkioc_free_util.h

This kernel helper header supports safe handling of the `DKIOCFREE` discard/free ioctl payload defined in `dkio.h`.

It defines `DFL_COPYIN_MAX_EXTS` as the maximum number of extents accepted during copyin and `DFL_ISSYNC()` to test whether a copied free list requested synchronous completion through `DF_WAIT_SYNC`.

`dkioc_free_info_t` stores normalized information needed to validate or translate a free-list request: flags, number of extents, structure sizes, extent offset fields, extent length fields, and total request size. This allows one implementation to handle native and model-specific layouts.

`dfl_iter_fn_t` is the callback type used when iterating normalized free-list extents. The declared helpers are `dfl_copyin()` to copy and validate user input, `dfl_free()` to release it, and `dfl_iter()` to iterate extents with a caller-supplied function.

Research notes:
- This file is kernel-only and exists to avoid open-coded `DKIOCFREE` copyin/parsing.
- The maximum extent count protects the kernel from excessive allocation.
- It depends directly on `dkioc_free_list_t` from `dkio.h`.
