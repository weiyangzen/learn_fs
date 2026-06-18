# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_cq.h

## Role

`tavor_cq.h` defines Tavor Completion Queue constants, software CQ state, CQE status/opcode values, and CQ operations exposed to IBTF and internal event processing.

## Major Definitions

The header defines default and minimal CQ counts/sizes for supported DDR profiles, CQ minimum size, `TAVOR_CQ_IS_SYNC_REQ()` for CQE DMA synchronization, and CQC entry size.

It enumerates CQE completion statuses for successful completions and local/remote errors, including length, operation, protection, flushed, bind, access, request, timeout, RNR NAK timeout, and unsupported RD-related errors. CQE type constants distinguish send RDMA write/read, send, atomic, bind, receive, and receive-with-immediate variants.

Macros map CQ numbers to completion EQs and CQ-error EQs. Error-CQE helpers define status, doorbell count, send/receive error opcodes, and recycling behavior. Special-QP tracking distinguishes normal and special CQs.

`tavor_sw_cq_s` stores CQ lock, consumer index, CQ number, CQE buffer, MR handle, size, sync flag, reference count, EQ numbers, special/user mapping flags, UAR page, devmap cookie, CQC and handle resources, callback argument, WRID AVL/tree state, reap list, and queue allocation info. `_NOTE` annotations document concurrency rules.

## Interfaces

The exported routines allocate, free, resize, arm/notify, poll, handle completion and error events, manage CQ reference counts, look up CQ handles by CQ number, and flush SRQ entries associated with a QP.

## Integration Notes

CQ state links hardware completion memory, event queues, IBTF callbacks, user mapping, and WRID lookup. CQE ownership and DMA sync behavior are performance-sensitive and depend on queue placement and mapping mode.
