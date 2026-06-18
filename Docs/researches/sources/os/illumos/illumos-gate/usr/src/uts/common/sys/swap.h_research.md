# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/swap.h

`swap.h` defines the `swapctl` ABI and kernel swap/anonymous-memory helpers. It rejects use of `swapctl` in 32-bit large-file compilation mode because the ABI structures use `off_t` directly.

`swapctl` commands include add, list, remove, get number of configured swap resources, and anonymous memory information (`SC_ADD`, `SC_LIST`, `SC_REMOVE`, `SC_GETNSWP`, `SC_AINFO`). User-visible structures describe requested swap resources (`swapres_t`), listed swap entries (`swapent_t`), and variable-length swap tables (`swaptbl_t`). 32-bit syscall views (`swapres32_t`, `swapent32_t`, `swaptbl32_t`) are defined for kernel compatibility.

Swap entry flags mark deletion in progress and deletion/re-add behavior (`ST_INDEL`, `ST_DOINGDEL`). Kernel `swapinfo` describes a configured swap area with byte offsets, vnode, next link, allocation counters, flags, total/free pages, path name, bitmap size and slots, allocation hint, and allocation-search counters.

The anon-slot mapping macros convert an anonymous-memory slot into a `(vnode, offset)` page identity. `swap_alloc()` derives a swapfs vnode index and page-aligned offset from the address of the anon slot, deliberately using low address bits for vnode selection to reduce page hash vnode mutex contention. `swap_xlate()` returns the stored vnode/offset and `swap_free()` is currently empty.

Kernel declarations expose physical swap allocation/free/name translation, anon lookup by vnode/offset, global `swapinfo`, and debug controls. `SWAP_PRINT` conditionally prints debug output for rename, reservation, allocation, and control categories.
