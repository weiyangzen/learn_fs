# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_iocb.h

## Purpose

Defines IOCB command opcodes, status/error encodings, and in-memory command/completion overlays for the Emulex `emlxs` Fibre Channel adapter driver. It covers legacy SLI-1/2/3 IOCB formats and bridges to SLI4 by embedding an `emlxs_wqe_t` in `emlxs_iocbq_t`.

## Main Definitions

- IOCB command constants for receive, transmit, ELS, abort/close XRI, FCP initiator, FCP target mode, adapter events, LP3000 BPL commands, SLI2 64-bit commands, SLI3 receive commands, and generic request/list commands.
- `PARM_ERR`: packed local/remote reject status detail fields with codes for fabric busy, port busy, LS_RJT, BA_RJT, and driver-local IO errors.
- `WORD5`: overlay for frame header control/status fields: `Rctl`, `Type`, `Dfctl`, `Fctl`.
- IOCB payload templates:
  - `GENERIC_RSP`
  - `XR_SEQ_FIELDS`
  - `ELS_REQUEST`
  - `RCV_ELS_REQ`
  - `AC_XRI`
  - `GET_RPI`
  - `FCPI_FIELDS`
  - `FCPT_FIELDS`
  - 64-bit variants such as `XMT_SEQ_FIELDS64`, `RCV_SEQ_FIELDS64`, `ELS_REQUEST64`, `RCV_ELS_REQ64`, `FCPI_FIELDS64`, `FCPT_FIELDS64`
  - `AUTO_TRSP`
  - `GENERIC_EXT_IOCB`
  - `RCV_SEQ_ELS_64_SLI3_EXT`
- `emlxs_iocb_t`: volatile 128-byte IOCB format with command-specific union, `ulpContext`/`ulpIoTag` overlays, command/status/owner bitfields, and SLI3 extension area.
- `emlxs_iocbq_t`: driver queue wrapper containing the IOCB, SLI4 WQE, linkage, back-pointers to buffers/port/channel/node/pkt, and flags.

## Integration Notes

This header is a hardware ABI surface. It depends on types defined elsewhere in the driver stack, including `ULP_BDE`, `ULP_BDE64`, `ULP_BDL`, `emlxs_wqe_t`, and driver private objects referenced through `void *` back-pointers.

The `emlxs_iocbq_t` wrapper is the object likely passed through driver queues; it binds the raw IOCB/WQE to software ownership and completion context.

## Risks and Gotchas

- Almost every packed control word has separate `EMLXS_BIG_ENDIAN` and `EMLXS_LITTLE_ENDIAN` layouts. Any include-order or platform macro error changes hardware-visible bit positions.
- Command numeric values intentionally overlap across SLI generations and contexts; consumers must interpret them with SLI mode and command path.
- The IOCB structure aliases fields through macros such as `ULPCONTEXT`, `ULPIOTAG`, `ULPCOMMAND`, `ULPSTATUS`, `RXFCHDR`, `RXSEQCNT`, and `RXSEQLEN`; refactoring should preserve exact offsets.
- Target-mode commands are present but conditional at use sites, not in this header.
