# File Research: sources/os/bsd/freebsd-src/sys/sys/chio.h

## Purpose
Defines the user/kernel ioctl ABI for SCSI media changer devices: moving media, exchanging media, positioning pickers, querying changer geometry, reading element status, and setting volume tags.

## Main Elements
- Element type IDs: `CHET_MT`, `CHET_ST`, `CHET_IE`, `CHET_DT`; comments warn that `sys/scsi/ch.c` relies on their numeric order.
- Command payloads: `changer_move`, `changer_exchange`, `changer_position`, `changer_params`.
- Element status ABI: `changer_voltag`, `changer_element_status`, `changer_element_status_request`, including SMC3 fields for medium type, protocol ID, association, designator type/code set, and designator bytes.
- Volume tag update ABI: `changer_set_voltag_request` with set, replace, clear, and alternate-tag flags.
- Ioctls: `CHIOMOVE`, `CHIOEXCHANGE`, `CHIOPOSITION`, `CHIOGPICKER`, `CHIOSPICKER`, `CHIOGPARAMS`, `CHIOIELEM`, `OCHIOGSTATUS`, `CHIOSETVOLTAG`, `CHIOGSTATUS`.

## Dependencies And Integration
Includes `sys/ioccom.h` and, outside the kernel, `sys/types.h`. It is consumed by changer drivers and userland tools that issue `ch(4)` ioctls.

## Risk Notes
This is ABI-sensitive. Struct layout, ioctl numbers, element type values, and fixed-size volume/designator buffers must remain compatible with existing userland and the SCSI changer driver.
