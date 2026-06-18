# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgcom.h

## Scope

Complete file read, 62 lines. This header defines the DKTP target-common transport object interface.

## Public Surface

It exports:

- `struct tgcom_obj`: common transport data pointer and operation table.
- `struct tgcom_objops`: init, free, packet creation/submission, transport, and reserved callbacks.
- Dispatch macros `TGCOM_INIT`, `TGCOM_FREE`, `TGCOM_PKT`, and `TGCOM_TRANSPORT`.

## Behavior And Integration

`tgcom` is the target-common layer that flow-control and disk target code use to convert buffers into command packets and send them into lower transport/controller code.

## Dependencies And Invariants

It assumes `opaque_t`, `struct buf`, `caddr_t`, and callback conventions. A `tgcom_obj` must be fully initialized before dispatch.

## Risks

Callbacks use unchecked function pointers and old-style callback signatures. Incorrect object wiring can corrupt the I/O path because `TGCOM_PKT` sits between buffers and transport submission.
