# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_event.h

## Role

`tavor_event.h` defines interrupt and event-queue support for the Tavor driver. It covers UAR doorbell writes, EQ sizing, event masks, catastrophic error identifiers, EQ software state, and event/interrupt processing entry points.

## Major Definitions

`TAVOR_UAR_DOORBELL()` performs 64-bit UAR writes. On 32-bit kernels it takes `ts_uar_lock` around `ddi_put64()` to preserve the hardware-required atomic write.

The file defines 64 total EQs, 47 used EQs, default EQ size, and `TAVOR_EQ_IS_SYNC_REQ()` for deciding whether EQE DMA sync is required. It also defines EQC entry size.

Event type constants and masks cover completions, path migration, communication established, send queue drained, CQ errors, local WQ/category errors, path migration failure, port state change, command completion, page faults, ECC detection, EQ overflow, invalid request/access violation WQ errors, and SRQ catastrophic/last-WQE events. `TAVOR_EVT_CATCHALL_MASK` catches selected error classes.

Additional constants control forced EQE sync, catastrophic error classification, and MSI programming.

`tavor_sw_eq_s` stores EQ consumer index, EQ number, EQE buffer, MR handle, size, sync flag, event mask, EQC and handle resources, handler function pointer, and queue allocation info.

## Interfaces

The file declares EQ initialization/finalization, EQ arming, the main ISR, EQ doorbell posting, and EQ overflow handling.

## Integration Notes

This header connects hardware interrupts, EQ memory, command completion events, CQ events, and asynchronous IBTF events. Its doorbell macro is architecture-sensitive because Tavor requires atomic 64-bit MMIO writes.
