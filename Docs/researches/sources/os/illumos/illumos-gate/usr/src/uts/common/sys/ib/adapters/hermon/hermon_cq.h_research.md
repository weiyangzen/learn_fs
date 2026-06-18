# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cq.h

## Purpose
Defines Completion Queue constants, CQE status/opcode values, CQ interrupt scheduling state, CQ software handle state, and CQ lifecycle/polling/event prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_CQ_SHIFT`
  - `HERMON_CQ_MIN_SIZE`
- CQE status constants map completion syndromes such as local length, protection, flushed WQE, remote access, retry, and RNR timeout errors.
- CQE send and receive opcode constants cover RDMA, send, atomic, LSO, FRWR, local invalidate, bind MW, and resize/error markers.
- `hermon_cq_sched_t`: assigns CQ handler IDs over interrupt/MSI EQ ranges.
- `struct hermon_sw_cq_s`: software CQ handle containing lock, consumer index, CQ number, buffer/MR/resource pointers, EQ numbers, user mapping state, doorbell record fields, interrupt moderation settings, handler argument, WRID tree, and queue allocation metadata.
- Prototypes cover allocation/free, resize, modify, notify, poll, scheduling, interrupt handlers, refcounts, lookup by CQ number, flush, and scheduler init/fini.

## Dependencies And Relationships
Includes `hermon_misc.h` for queue allocation and shared driver definitions. CQ handlers consume EQEs from `hermon_event.h`/`hermon_hw.h`; QP and WRID code depend on CQ state for completion processing.

## Research Notes
The header documents separate EQ assignment for normal completions and CQ errors. Lock annotations split immutable CQ fields, lock-protected fields, and deliberately shared moderation/resize state.
