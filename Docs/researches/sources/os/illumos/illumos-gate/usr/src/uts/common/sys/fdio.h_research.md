# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdio.h

## Purpose

`fdio.h` defines the public floppy disk ioctl ABI: media/drive characteristics, raw controller commands, direct floppy commands, and disk-change reporting.

## Main Types

`struct fd_char` describes floppy media geometry: medium type, transfer rate, cylinders, heads, sector size, sectors per track, and stepping.

`struct fd_state` returns current device state such as bytes per sector, sectors per track, step rate, data rate, and controller error.

`struct fd_drive` describes drive hardware timing/capability parameters including ejectability, search table size, write precompensation, step timing, head load/unload timing, motor timing, pin semantics, and flags.

`struct fd_search` passes a table of candidate `fd_char` entries.

`struct fd_cmd` describes a high-level floppy command with command code, flags, block number, sector count, user buffer address, and buffer length. `struct fd_cmd32` is the 32-bit syscall ABI variant.

`struct fd_raw` passes raw command/result bytes and an optional transfer buffer. `struct fd_raw32` is the 32-bit ABI variant.

## Interfaces and Constants

Disk-change flags include `FDGC_HISTORY`, `FDGC_CURRENT`, `FDGC_CURWPROT`, and `FDGC_DETECTED`.

Drive flags include `FDD_READY`, `FDD_MOTON`, and `FDD_POLLABLE`.

High-level commands include read, write, seek, rezero, format unit, and format track.

Execution flags include `FD_SILENT`, `FD_DIAGNOSE`, `FD_ISOLATE`, `FD_READ`, and `FD_WRITE`.

Raw controller opcodes include specify, read ID, sense drive, rezero, seek, sense interrupt, format, read/write commands, and deleted-data variants.

Ioctls include `FDIOGCHAR`, `FDIOSCHAR`, `FDEJECT`, `FDGETCHANGE`, `FDGETDRIVECHAR`, `FDSETDRIVECHAR`, `FDGETSEARCH`, `FDSETSEARCH`, `FDIOCMD`, `FDRAW`, and `FDDEFGEOCHAR`.

## Research Notes

This header is the stable control interface through which userland and filesystem helpers can query and manipulate floppy block-device geometry and media state. It is included by PCFS code in this tree.
