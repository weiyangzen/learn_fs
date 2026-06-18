# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_debug.h

This header declares the NFSv4.1 driver debug helper API and tracing macros.

It declares debug printers, RDBSS object printers, IRP/IOCTL decoders, create-parameter and information-class decoders, hex dumping, opcode/status helpers, ACL argument printing, and `dprintk`.

Macros:
- `_DRIVER_NAME_` is `NFS4.1 Driver`.
- `DbgEn`, `DbgEx`, and `DbgR` wrap function entry/exit logging with PSEH exception handling.
- `DBG_ERROR`, `DBG_WARN`, `DBG_TRACE`, `DBG_INFO`, `DBG_DISP_IN`, and `DBG_DISP_OUT` define debug flag bits.
- `PNFS_TRACE_TAG` and `PNFS_FLTR_ID` identify the mini-redirector trace stream.
- `DbgEnter` and `DbgExit` emit dispatch entry/exit traces.

Research notes:
- The `DbgEx` macro assumes a local `status` variable exists.
- The macros use PSEH blocks, matching the driver’s ReactOS kernel build environment.
- This header is coupled to RDBSS types and NFS driver constants declared outside this file.
