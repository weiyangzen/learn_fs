# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddidmareq.h

This header defines DMA object descriptions, DMA limits/attributes, DMA request structures, mapping flags, return codes, synchronization flags, legacy DMA control ops, and I/O memory cache attributes.

DMA source/destination objects can be virtual addresses, page lists, physical addresses, buffer virtual addresses, or DVMA addresses. The object model is represented by `v_address`, `pp_address`, `phy_address`, `dvma_address`, `ddi_dma_aobj_t`, `ddi_dma_atyp_t`, and `ddi_dma_obj_t`.

DMA limits are architecture-specific. SPARC `ddi_dma_lim_t` describes low/high DMA address range, counter maximum, burst sizes, minimum transfer, and expected DMA speed. x86 extends this with versioning, address register max, count register max, granularity, scatter/gather length, and request size, with `DMA_UNIT_8/16/32` and `DMALIM_VER0`.

Modern `ddi_dma_attr_t` describes DMA address range, counter limit, alignment, burst sizes, minimum and maximum transfer, segment boundary, scatter/gather length, granularity, and bus-specific flags. Attribute flags include forced physical DMA, error flagging, relaxed ordering, and a private bounce-on-segment flag.

`ddi_dma_req_t` packages optional limits, allocation flags, callback/sleep behavior, callback argument, and the DMA object. Callback constants distinguish no-wait, sleep, and callback-based resource wait; callback return values indicate runout or done.

DMA mapping flags include read/write direction, redzone, partial mapping, consistent mapping, exclusive mapping, streaming, and SBus 64-bit support. Return codes distinguish mapped, partial, done, no resources, no mapping, too big/small, locked, bad limits, stale, bad attributes, in use, and physical-DMA fallback.

Synchronization flags specify consistency for device, CPU, or kernel view. The `ddi_dma_ctlops` enum preserves many obsolete bus nexus control operations plus resource reserve/release, SBus64, remap, and motherboard DMA engine operations. Cache attribute flags define cached, write-combining, and uncached I/O memory behavior with helper macros.

Research notes:
- This file is foundational for both old and newer DDI DMA APIs.
- ABI varies by architecture, especially `ddi_dma_lim_t`.
- Many enum members are explicitly obsolete but remain required by bus ops and legacy callers.
- Cache-attribute flags are mutually exclusive and used to override HAT attributes.
