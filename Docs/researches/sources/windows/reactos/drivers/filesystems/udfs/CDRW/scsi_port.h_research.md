# File Research: sources/windows/reactos/drivers/filesystems/udfs/CDRW/scsi_port.h

## Purpose

`scsi_port.h` is a local SCSI port compatibility header. It defines SCSI port IOCTLs, pass-through structures, inquiry/capability/address records, and class-driver helper prototypes for environments that need these definitions in the CDRW/UDFS stack.

## Main Contents

- Includes `srb.h`.
- Defines `IOCTL_SCSI_BASE` and the `\\Device\\ScsiPort` name prefix.
- Defines SCSI port IOCTLs:
  - pass-through and direct pass-through.
  - miniport, inquiry data, capabilities, address, rescan bus, dump pointers.
- Defines structures:
  - `SCSI_PASS_THROUGH` and `SCSI_PASS_THROUGH_DIRECT`.
  - `SCSI_BUS_DATA`, `SCSI_ADAPTER_BUS_INFO`, `SCSI_INQUIRY_DATA`.
  - `SRB_IO_CONTROL`.
  - `IO_SCSI_CAPABILITIES`.
  - `SCSI_ADDRESS`.
  - `DUMP_POINTERS`.
- Defines pass-through direction values: data out, data in, unspecified.
- Declares SCSI class helper routines in kernel mode:
  - inquiry/capacity reads, capability/address queries, queue release, device claim/remove, internal IO control, completion, synchronous SRB send, SRB bus address initialization.
- Declares `DbgWaitForSingleObject_`.

## Integration Notes

The CDRW layer can use this header to submit SCSI pass-through requests or interact with class/port driver helpers without depending on a specific platform SDK version.

## Risks And Edge Cases

- This is a compatibility copy of sensitive kernel storage APIs. Divergence from the platform’s real SCSI headers can cause ABI mismatches.
- Direct pass-through contains a kernel pointer field, so it is only safe when used in the correct caller mode and IOCTL method context.
- Helper prototypes are suppressed for `USER_MODE` and partially for `CDRW_W32`; call sites must honor those build modes.
