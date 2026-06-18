# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_event.h

## Purpose
Defines interrupt/event queue support: UAR doorbell write macros, doorbell record writes, EQ defaults, event IDs and masks, catastrophic error codes, EQ arm/register offsets, EQ software handle state, and event processing prototypes.

## Main Interfaces
- `HERMON_UAR_DOORBELL()` handles 64-bit doorbell writes, using `hs_uar_lock` only on 32-bit kernels to protect non-atomic 64-bit access.
- `HERMON_UAR_DB_RECORD_WRITE()` writes host-memory doorbell records in network byte order.
- EQ defaults:
  - `HERMON_NUM_EQ_SHIFT`, `HERMON_NUM_EQ`
  - `HERMON_NUM_EQ_USED`
  - `HERMON_DEFAULT_EQ_SZ_SHIFT`
  - `HERMON_EQ_CI_MASK`
- Event IDs and masks include completions, QP async events, CQ errors, SRQ events, port state, command completion, catastrophic/local errors, GPIO, spoof failure, and FEXCH errors.
- `struct hermon_sw_eq_s`: software EQ handle with consumer index, EQ number, EQ buffer/doorbell, MR/resource pointers, event mask, handler callback, and queue allocation metadata.
- Prototypes cover EQ init/fini/arm, ISR, doorbell posting, overflow handling, and UAR base reset.

## Dependencies And Relationships
Used by command completion, CQ completion/error processing, async IB event processing, and catastrophic error handling. Hardware EQE formats are defined in `hermon_hw.h`.

## Research Notes
The owner-bit logic for EQEs lives in `hermon_hw.h`; this file defines higher-level event categories and the software EQ state that event handlers consume.
