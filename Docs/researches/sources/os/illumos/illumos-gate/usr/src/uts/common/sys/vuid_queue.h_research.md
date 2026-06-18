# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_queue.h

## Role

`vuid_queue.h` defines the public interface for a small queue package that stores pending `Firm_event` VUID input events.

## Key Structures

`Vuid_queue` holds:
- top and bottom queue nodes,
- a free-list pointer,
- current item count,
- queue capacity.

Macros expose used count, available capacity, size, empty state, and full state.

`Vuid_q_node` stores next/previous links and one `Firm_event`.

Status codes are:
- `VUID_Q_OK`
- `VUID_Q_OVERFLOW`
- `VUID_Q_EMPTY`

## Functions

The header declares old-style unprototyped functions for:
- queue initialization over caller-provided storage,
- putting events into timestamp-dependent queue position,
- getting and peeking,
- putting an event back at the top,
- compressing valuator events,
- identifying valuator events,
- deleting a node.

## Research Notes

The queue owns no allocation; callers provide and later release the backing storage. Compression is designed for input-event streams where high-frequency valuator updates can be collapsed.
