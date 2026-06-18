# File Research: sources/os/bsd/netbsd-src/sys/sys/chio.h

## Scope

Defines media changer ioctl ABI for robotic storage devices.

## APIs And Data Structures

- Element type constants: picker, slot, import/export portal, and drive.
- Request structs cover move medium, exchange medium, position picker, changer parameters, element status, and volume tag modification.
- Status structs describe fullness, access, exception state, source element, volume tags, vendor data length, SCSI sense fields, and drive target/LUN.
- Defines status validity flags and per-element masks.
- Defines changer event bitmask size and `CHEV_ELEMENT_STATUS_CHANGED`.
- Ioctls include move, exchange, position, get/set picker, get params, initialize element status, old/new get status, and set volume tag.

## Dependencies

- Includes `sys/ioccom.h`.

## Risks And Invariants

- Element type numeric values are used as array offsets by the SCSI changer driver and must not change.
- Pointer fields in ioctl structs require compat handling across user/kernel and ABI widths.
