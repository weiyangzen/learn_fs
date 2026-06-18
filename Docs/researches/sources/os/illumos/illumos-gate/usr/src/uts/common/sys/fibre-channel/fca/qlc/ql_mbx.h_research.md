# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_mbx.h

## Role

`ql_mbx.h` defines the mailbox command/status interface for the illumos `qlc` QLogic ISP2xxx Fibre Channel adapter driver. Mailbox commands are the driver’s control path into firmware for initialization, link management, diagnostics, flash access, fabric login/logout, resets, resource queries, and extended 8xxx/82xx features.

## Major Definitions

The file groups firmware status and event constants:
- ROM/self-test states, firmware running/config errors, and command completion statuses.
- Sub-error codes for mailbox command errors.
- Asynchronous event codes for reset, system errors, request/response transfer errors, LIP/link changes, port database updates, RSCN, SCSI/IP/CTIO completions, DCBX/FCF updates, temperature events, D_Port diagnostics, IDC events, SFP insertion/removal, NIC firmware state, and autoload firmware events.
- Event-specific reason fields for port database updates, RSCN scope, thermal alerts, D_Port diagnostics, and Menlo alerts.

Mailbox command opcodes include:
- Firmware load/execute/dump/read/write/checksum commands.
- Abort, target reset, LUN reset, clear/abort task set commands.
- Loop, fabric, port database, login/logout, SNS, RNID, link status, and FC_AL commands.
- IP initialization/unload and XGMAC/statistics commands.
- Flash access, SFP, SERDES, LED, DCBX, FCF, IDC, port reset/config, mini-dump template, and 82xx interrupt toggling commands.

The header defines command option masks and data structures:
- `mbx_cmd_t` for mailbox command descriptors.
- Diagnostic `echo_t`.
- Loop Fabric Address command payloads.
- 23xx and 24xx port database layouts.
- Port database state values and helper macro `PD_PORT_LOGIN`.
- Link configuration fields for pause, DCBX, loopback, backplane training, autonegotiation, and jumbo frames.
- FCF list descriptor `ql_fcf_list_desc_t`.

## Interfaces

The prototypes cover the complete mailbox-control surface:
- IP bring-up/shutdown, online self-test, loopback, ELS echo, and LFA/change requests.
- SCSI task management and target/LUN resets.
- Loop/fabric login, logout, port database fetches, loop maps, RNID, link status/statistics, LIP, and ID list operations.
- RISC RAM word/block read/write, mailbox IOCB execution, mailbox wrap test, firmware execution/init/state/version/options.
- Diagnostics for loopback, echo, beacon, SERDES, SFP, firmware tracing, Menlo reset, MPI restart, IDC, port config, flash access, XGMAC stats, DCBX, FCF, resource counts, mini-dump template, flash image load, LED config, remote register access, temperature, and SERDES read/write.
- `MBOX_CMD_TABLE()` maps mailbox opcodes to printable command names for logging/debugging.

## Integration Notes

This is one of the central firmware ABI headers for `qlc`. Constants are shared by ISR, initialization, firmware, flash, diagnostic, and ioctl paths. Many numeric values are reused by different hardware generations, so callers must interpret command/event values in adapter-generation context.
