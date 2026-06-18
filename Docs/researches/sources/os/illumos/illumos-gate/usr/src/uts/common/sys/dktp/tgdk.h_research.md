# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/tgdk.h

## Scope

Complete file read, 175 lines. This header defines the target disk object interface for DKTP disk drivers.

## Public Surface

It exports:

- `struct tgdk_ext`: removable/read-only flags, node type, and controller type.
- `struct tgdk_obj`: target object data, operations, extension pointer, and embedded extension storage.
- `struct tgdk_iob`: I/O-buffer handle with buffer, logical block, transfer length, physical sector, byte count/offset, and flags.
- `IOB_BPALLOC` and `IOB_BPBUFALLOC`.
- `struct tgdk_geom`: cylinder/head/sector/sector-size/capacity geometry.
- `struct tgdk_objops`: callbacks for lifecycle, probe/attach/open/close/ioctl/strategy, geometry, I/O-buffer allocation/free/transfer, dump, physical geometry, bad-block object setup, media check, inquiry, cleanup, and reserved slot.
- `dadk_create()` factory prototype.
- Attribute and dispatch macros for all target-disk operations.
- `LBLK2SEC()`, `SETBPERR`, and `DK_MAXRECSIZE`.

## Behavior And Integration

This is the main abstract target disk API used by common disk code. `cmdk` can call `TGDK_*` macros to perform disk operations through a concrete implementation such as `dadk`.

## Dependencies And Invariants

The object pointer must be a valid `struct tgdk_obj *`; `tg_ext` and `tg_ops` must be initialized. Geometry and capacity fields must use consistent sector sizes and shifts. `DK_MAXRECSIZE` caps I/O record size at 256 KiB.

## Risks

`TGDK_INIT` and `TGDK_INIT_X` both dispatch to `tg_init` but with different argument counts, while the declared function pointer takes six arguments; the extended macro relies on implementation/prototype compatibility outside this header. All dispatch macros bypass type and null checks.
