# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/cmpkt.h

## Scope

Complete file read, 80 lines. This header defines the common command packet exchanged between DKTP target and controller layers.

## Public Surface

It exports `struct cmpkt`, with fields for:

- Generic controller, controller-private, and device-private pointers.
- Status block and command block pointers/lengths.
- Completion reason, callback, timeout, and flags.
- Associated `struct buf`, residual byte tracking, bytes left, bytes transferred in the current disk section.
- Starting sector, sectors left, retry count, target iodone callback, fault-recovery packet, private data, and pass-through command pointer.

It defines completion reasons `CPS_SUCCESS`, `CPS_FAILURE`, `CPS_CHKERR`, and `CPS_ABORTED`, plus flag `CPF_NOINTR`.

## Behavior And Integration

`cmpkt` is the central I/O command descriptor passed through controller ops, target disk ops, flow-control queues, and generic disk adapter helpers. The file provides layout and constants only.

## Dependencies And Invariants

The header assumes `opaque_t`, `daddr_t`, and `struct buf` are known through includers. Packet owners must keep status/command block lengths synchronized with their pointed data.

## Risks

Callbacks use old-style `void (*)()` prototypes, so type checking is weak. Multiple private pointers make ownership ambiguous unless each layer follows the DKTP contract. Sector and byte counters use `long`/`daddr_t`, so overflow behavior depends on platform width and request splitting.
