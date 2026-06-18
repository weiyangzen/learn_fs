<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h -->
# sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h

## Purpose

`smb2_fio.h` is the narrow public header for the PS2 SMB2 filesystem adapter. It exposes the driver initialization entry used by the IRX module start function.

## Important APIs, Types, And Functions

The only declaration is `int SMB2_initdev(void);`, protected by include guard `__SMB2_FIO_H__`.

## Control Flow

There is no control flow in the header. `smb2man.c` calls `SMB2_initdev()` from `_start`, which then registers the `smb` IOP driver in `smb2_fio.c`.

## State And Persistence Behavior

No state is defined. The global device and share state live in `smb2_fio.c`.

## Dependencies And Integration Points

It is included by `smb2man.c` and implemented by `smb2_fio.c`. Keeping this header small limits the IRX module entry dependency on the rest of the driver internals.

## Risks And Edge Cases

The header gives no visibility into cleanup or devctl APIs, so external callers must know the PS2 device contract from `ps2smb2.h` or IOMAN. If `SMB2_initdev` changes signature, module startup breaks at compile time.

## Test Signals

Build tests should verify `smb2man.c` links against `SMB2_initdev` and that duplicate declarations do not drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/smb2_fio.h -->
