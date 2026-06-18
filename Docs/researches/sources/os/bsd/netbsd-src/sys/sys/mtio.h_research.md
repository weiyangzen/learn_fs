# File Research: sources/os/bsd/netbsd-src/sys/sys/mtio.h

## Purpose
Defines magnetic tape ioctl structures, operation codes, device type/status constants, and kernel minor-device bit layout.

## Main API
- Command structures: `struct mtop`, `struct mtget`.
- Tape operations: `MTWEOF`, `MTFSF`, `MTBSF`, `MTFSR`, `MTBSR`, `MTREW`, `MTOFFL`, `MTNOP`, `MTRETEN`, `MTERASE`, `MTEOM`, `MTNBSF`, `MTCACHE`, `MTNOCACHE`, `MTSETBSIZ`, `MTSETDNSTY`, `MTCMPRESS`, `MTEWARN`.
- Status/type constants: `MT_IS*`, `MT_DS_RDONLY`, `MT_DS_MOUNTED`.
- Ioctls: `MTIOCTOP`, `MTIOCGET`, `MTIOCIEOT`, `MTIOCEEOT`, `MTIOCRDSPOS`, `MTIOCRDHPOS`, `MTIOCSLOCATE`, `MTIOCHLOCATE`.
- Kernel minor bits: `T_UNIT`, `T_NOREWIND`, `T_DENSEL`, density selectors.

## Dependencies
Uses `sys/ioccom.h` for ioctl encoding.

## Risks and Notes
The header notes that status registers are device-dependent and SCSI sense information does not fit cleanly into `mt_erreg`. 32-bit block-position ioctls are legacy-shaped and may not cover newer large tape command models.
