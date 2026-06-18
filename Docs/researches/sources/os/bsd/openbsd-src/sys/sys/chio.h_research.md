# File Research: sources/os/bsd/openbsd-src/sys/sys/chio.h

This header defines the changer/tape-library ioctl interface.

Key definitions:
- Element types: `CHET_MT`, `CHET_ST`, `CHET_IE`, `CHET_DT`.
- Operation structures: `changer_move`, `changer_exchange`, `changer_position`, `changer_params`, `changer_voltag`, `changer_element_status`, and `changer_element_status_request`.
- Status bits: `CESTATUS_FULL`, `CESTATUS_IMPEXP`, `CESTATUS_EXCEPT`, `CESTATUS_ACCESS`, `CESTATUS_EXENAB`, `CESTATUS_INENAB`, plus per-element masks.
- Ioctls: `CHIOMOVE`, `CHIOEXCHANGE`, `CHIOPOSITION`, `CHIOGPICKER`, `CHIOSPICKER`, `CHIOGPARAMS`, `CHIOGSTATUS`.

Behavior and integration:
- Element type numeric values are ABI-sensitive and used as offsets by `sys/scsi/ch.c`.
- `CHIOGSTATUS` passes a caller-allocated array pointer through `changer_element_status_request`.

Risk notes:
- Reordering element type constants would break the SCSI changer driver.
- Status-return ioctls require careful count/type validation by consumers because the request contains a raw pointer.
