# File Research: sources/windows/reactos/drivers/filesystems/ntfs/misc.c

## Purpose

`misc.c` contains small shared utility routines for NTFS IRP setup, top-level IRP tracking, NTFS-to-Windows attribute conversion, and user-buffer access/locking.

## Main Functions

`NtfsIsIrpTopLevel`

- Checks `IoGetTopLevelIrp()`.
- If no top-level IRP is set, installs the current IRP and returns `TRUE`.
- Otherwise returns `FALSE`.

`NtfsAllocateIrpContext`

- Allocates an `NTFS_IRP_CONTEXT` from the global IRP-context lookaside list.
- Initializes identifier, IRP, device object, stack location, major/minor function, file object, top-level state, priority boost, and default completion flag.
- Sets `IRPCONTEXT_CANWAIT` for filesystem control, device control, shutdown, synchronous operations, and most non-cleanup/non-close requests.

`NtfsFileFlagsToAttributes`

- Converts NTFS file attribute flags into Win32 file attributes.
- Maps `NTFS_FILE_TYPE_DIRECTORY` to `FILE_ATTRIBUTE_DIRECTORY`.
- Produces `FILE_ATTRIBUTE_NORMAL` when the NTFS attribute mask is zero.

`NtfsGetUserBuffer`

- Returns a system address for an MDL-backed IRP buffer with `MmGetSystemAddressForMdlSafe`.
- Otherwise returns `Irp->UserBuffer`.
- Uses higher page priority for paging I/O.

`NtfsLockUserBuffer`

- Ensures an IRP has an MDL for its user buffer.
- Allocates an MDL if needed and probes/locks pages with the requested `LOCK_OPERATION`.
- Uses SEH to free the MDL and return the exception code if probing fails.

## Integration

These helpers are used by dispatch and read/write code. `NtfsAllocateIrpContext` creates the common request state consumed by all NTFS major-function handlers, while `NtfsGetUserBuffer` and `NtfsLockUserBuffer` are used directly in `rw.c`.

## Notable Behavior

- `NtfsGetUserBuffer` returns raw `Irp->UserBuffer` when no MDL exists, so callers must know whether direct, buffered, or neither I/O is in effect.
- `NtfsLockUserBuffer` leaves successful MDL unlock/free responsibility to the I/O manager or later IRP cleanup.
