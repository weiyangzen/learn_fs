# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/flowctrl.h

## Scope

Complete file read, 72 lines. This header defines the DKTP flow-control object interface.

## Public Surface

It exports:

- `struct flc_obj`: object data pointer plus operation table.
- `struct flc_objops`: callbacks for init, free, enqueue, dequeue, kstat start, kstat stop, and reserved slots.
- Factory prototypes `dsngl_create()`, `dmult_create()`, `duplx_create()`, and `adapt_create()`.
- Dispatch macros `FLC_INIT`, `FLC_FREE`, `FLC_ENQUE`, `FLC_DEQUE`, `FLC_START_KSTAT`, and `FLC_STOP_KSTAT`.

## Behavior And Integration

The flow-control object mediates buffering and outstanding I/O limits between target common transport and queue objects. Different factories create single, multiple, duplex, or adapter-specific flow-control policies.

## Dependencies And Invariants

The interface assumes `opaque_t`, `struct buf`, and the DKTP object model are available. Objects must have initialized `flc_data` and `flc_ops`.

## Risks

Factory prototypes are old-style declarations without explicit parameter lists. Dispatch macros are unchecked and can call null or mismatched callbacks if object initialization fails.
