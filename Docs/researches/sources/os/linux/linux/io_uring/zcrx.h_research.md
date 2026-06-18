# File Research: sources/os/linux/linux/io_uring/zcrx.h

## Purpose
Defines the internal io_uring zero-copy receive data structures, feature/flag masks, and public internal entry points used by io_uring receive and registration code.

## Main Contents
- `io_zcrx_mem` stores imported memory state: size, pinned pages, sg table, memory-accounting pages, dma-buf attachment, and dma-buf handle.
- `io_zcrx_area` groups a `net_iov_area`, per-niov user references, freelist state, mapping state, area ID, and backing memory.
- `zcrx_rq` describes the userspace return queue ring and cached head.
- `io_zcrx_ifq` ties one io_uring ZCRX context to an area, return queue, user/mm accounting, optional netdev/RX queue/DMA device, refcounts, page-pool lock, and mmap region.
- Compile-time stubs return `-EOPNOTSUPP` when `CONFIG_IO_URING_ZCRX` is disabled.

## Integration Points
Included by io_uring receive and registration implementation. Depends on io_uring types, dma-buf declarations, socket declarations, page-pool types, and netdev tracker state.

## Notable Behaviors
- `ZCRX_SUPPORTED_REG_FLAGS` admits import and no-device registration modes.
- `ZCRX_FEATURES` currently advertises receive page-size support.
- `user_refs` counts userspace-facing references separately from the internal object lifetime refcount.

## Risks And Review Focus
- Layout changes must remain consistent with `zcrx.c` lifetime rules and UAPI registration behavior.
- Stub behavior must match callers that expect unsupported ZCRX to fail cleanly.
