# File Research: sources/virtualization/qemu/block/nvme.c

## Purpose
Implements QEMU's `nvme` block protocol driver for direct access to a physical NVMe PCI device through VFIO. It maps BAR registers, initializes admin and I/O queue pairs, submits NVMe commands, maps guest I/O buffers for DMA, and exposes the device through QEMU's coroutine block driver interface.

## Main Entry Points
- `nvme_parse_filename()` parses `nvme://PCIADDR/NSID` into runtime options.
- `nvme_open()` validates options, initializes the controller with `nvme_init()`, and optionally configures write-cache behavior for `BDRV_O_NOCACHE`.
- `nvme_init()` opens the PCI device through VFIO, maps BAR0, resets/enables the controller, creates admin queues, enables MSI-X, identifies the controller/namespace, and creates an I/O queue.
- `nvme_close()` tears down queues, event notifiers, BAR mappings, VFIO state, and saved device name.
- `nvme_co_preadv()`, `nvme_co_pwritev()`, `nvme_co_flush()`, `nvme_co_pwrite_zeroes()`, and `nvme_co_pdiscard()` implement the block I/O operations.

## Internal Mechanics
Queue state is split into `NVMeQueuePair`, `NVMeQueue`, and `NVMeRequest`. Each queue pair owns DMA-mapped submission/completion queues, one page of PRP-list memory per request, a free-request list, a completion bottom half, and coroutine wait queues for request exhaustion. The admin queue is index 0; I/O queues start at index 1. The driver currently creates one I/O queue.

Command submission fills an SQ entry under the queue lock, assigns the request CID, increments `need_kick`, and defers the doorbell write through `defer_call()`. Completion processing runs in the block node's main `AioContext`, checks the CQ phase bit, translates NVMe status to errno, returns request slots to the freelist, invokes callbacks outside the queue lock, updates the CQ head doorbell, and wakes coroutines waiting for free request slots.

DMA handling maps aligned qiov buffers into VFIO IOVA space and builds NVMe PRP entries. If VFIO mapping returns ENOSPC/ENOMEM because temporary DMA mappings are exhausted, coroutines coordinate through `dma_map_lock` and `dma_flush_queue` to reset temporary mappings once outstanding DMA mappings drain. Unaligned qiovs are copied through an aligned temporary buffer.

Controller identification records namespace size, LBA shift, write-cache support, maximum transfer size, write-zeroes support, discard support, and namespace metadata restrictions. Block limits are refreshed from page size, LBA size, MDTS, and NVMe command field limits.

## Dependencies
Uses QEMU VFIO helpers, host PCI MMIO helpers, event notifiers, AioContext/BH APIs, coroutine queues and mutexes, NVMe protocol definitions from `block/nvme.h`, and QEMU block driver interfaces. It depends on Linux VFIO and a PCI NVMe device address supplied by the user.

## Filesystem/Block Relevance
This is a virtual block integration layer that exposes real NVMe hardware directly to QEMU's block layer. It is important for understanding how QEMU maps block I/O requests into hardware queue commands, handles DMA registration pressure, advertises discard/write-zeroes/flush semantics, and enforces strict alignment requirements.

## Risks and Notes
- The driver relies on careful AioContext separation: command submission may happen from any context, but kicking and completion processing happen in the BDS main context.
- Request freelist, SQ/CQ indices, `need_kick`, and `inflight` are protected by the queue lock; callbacks are invoked outside the lock to permit re-entrancy.
- Temporary DMA mappings are intentionally reclaimed lazily; failures before `dma_map_count` increments rely on later reset paths to reclaim any partial mappings.
- Only namespaces without metadata are supported.
- The driver blocks resize/grow operations and only accepts no-op truncation.
- `nvme_register_buf()` notes a FIXME that fixed mappings can exhaust IOVA space after repeated register/unregister cycles.
