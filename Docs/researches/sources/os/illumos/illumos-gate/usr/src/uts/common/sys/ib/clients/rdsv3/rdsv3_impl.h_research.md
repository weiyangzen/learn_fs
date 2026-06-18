# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_impl.h

This Solaris-only RDSv3 implementation header provides Linux-compatibility primitives and illumos helper declarations used by the OFED-derived RDSv3 code.

Core definitions:
- Big-endian typedefs map to native integer types.
- Atomic compatibility maps Linux-style `atomic_t`, compare/exchange, decrement-test, bit operations, and little-endian bit operations onto illumos atomics.
- Timing/page constants emulate Linux-style `jiffies`, `HZ`, `PAGE_SIZE`, and bit widths.
- Error-pointer macros emulate Linux `ERR_PTR`, `IS_ERR`, and `PTR_ERR`.
- List macros add remove/splice and safe iteration helpers over illumos lists.
- `rdsv3_wait_queue_t` emulates Linux wait queues with mutex/CV/waiter count and wait/wake macros.
- `rsock_t` is an internal socket shim with upper handle/upcalls, lock, flags, sleep wait queue, send/receive buffers, refcount, and protocol info.
- Workqueue and delayed-work structs emulate Linux work items using illumos locks, timeouts, and list queues.
- `rdsv3_scatterlist` maps a virtual address/length to IBT SGL and mapping handle.
- Control-message macros provide CMSG alignment/traversal without depending on XPG guard exposure.
- OFUV-to-IB helper macros extract IBTF handles from OFED wrapper objects.
- `rdsv3_hdrs_mr` describes registered header memory.

API surface:
- Transport init, interface/IP ioctl helpers, delayed work/workqueue operations, socket allocation/init/exit, connection constructors/comparators, loop init, MR compare, cmsg put, bind verification, checksum, DMA map/unmap, and socket ref/flag helpers.

Risk-sensitive invariants:
- `PAGE_SIZE` is hardcoded to 4096 with a comment noting this is a workaround.
- Wait macros increment/decrement waiter counts around CV waits and require condition predicates to be stable under the wait queue mutex.
- Linux compatibility bit operations differ for SPARC little-endian bitmap indexing through `LE_BIT_XOR`.
