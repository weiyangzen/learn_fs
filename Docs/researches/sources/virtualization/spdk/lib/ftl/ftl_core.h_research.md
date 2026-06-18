# File Research: sources/virtualization/spdk/lib/ftl/ftl_core.h

## Purpose
Defines the central `struct spdk_ftl_dev` runtime object and core helper APIs.

## Device State
`struct spdk_ftl_dev` contains configuration, layout, superblocks, IO-channel list, base device descriptor/type, NV cache, mempools, statistics, bands, free/shut lists, L2P state, valid/trim maps, writers, relocation, core thread/poller, queues, P2L checkpoint lists, layout trackers, and configurable properties.

## Key Constants
- `P2L_MEMPOOL_SIZE` reserves P2L buffers for open/close and relocation.
- `FTL_ZERO_BUFFER_SIZE` defines a 1 MiB DMA buffer used to avoid NULL metadata-buffer problems on some devices.

## Inline Helpers
Provides band count/block count, core-thread checks, FTL address packing and NV-cache address conversion, sequence ID allocation, P2L/tail metadata sizing, and fast-startup/fast-recovery predicates based on clean flags and shared-memory readiness.

## API
Declares limit application, address invalidation, pollers, relocation threshold checks, free-band selection, trim map updates, max sequence recovery, stats helpers, and trim entry point.

## Dependencies
Includes SPDK uuid/thread/bdev/ftl and most internal FTL headers.
