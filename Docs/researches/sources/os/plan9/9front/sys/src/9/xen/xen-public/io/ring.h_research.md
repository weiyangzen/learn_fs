# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/ring.h

Imported Xen public shared-ring macro framework.

Purpose:
- Defines generic producer/consumer ring types and manipulation macros used by Xen split device protocols.

Key content:
- Defines `RING_IDX` and helpers to round ring capacity down to a power of two.
- Defines `DEFINE_RING_TYPES` to generate shared ring, frontend ring, and backend ring structs.
- Defines shared/front/back initialization macros.
- Defines ring size/free/full/unconsumed checks and direct request/response element access.
- Defines overflow checks for request indexes.
- Defines push macros with memory barriers.
- Defines notification hold-off macros using `req_event` and `rsp_event`, including final checks before sleeping.

Integration:
- Directly used by `blkif.h`, `netif.h`, `fsif.h`, `usbif.h`, `vscsiif.h`, and `mem_event.h`.
- 9front’s `sdxen.c` and `etherxen.c` depend on these generated ring types and macros for block and network I/O.

Risks/notes:
- Explicitly provides no interlocks or flow control beyond the ring accounting; caller must enforce outstanding-request limits.
- Memory barriers are essential for cross-domain visibility.
- Ring sizes are power-of-two masked; corrupt producer indexes can cause overflow bugs if not checked.
