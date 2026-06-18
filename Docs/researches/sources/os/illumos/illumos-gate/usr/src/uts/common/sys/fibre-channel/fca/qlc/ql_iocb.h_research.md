# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_iocb.h

## Role

`ql_iocb.h` defines the hardware IOCB contract for the illumos `qlc` QLogic ISP2xxx Fibre Channel adapter driver. It is a protocol/header file rather than executable logic: it names queue entry opcodes, fixed DMA descriptor layouts, status values, and the prototypes used by `ql_iocb.c` to build request queue entries.

## Major Definitions

The file starts with generic 32-bit and 64-bit DMA data segment layouts, then defines many IOCB formats used by different hardware generations and modes.

Initiator command formats include:
- Type 2 32-bit SCSI command IOCBs with extended LUN support.
- Type 3 64-bit command IOCBs.
- Type 6 and Type 7 ISP24xx command IOCBs.
- FCP command DMA layout for Type 6 commands.
- Command chaining and continuation entries for scatter/gather lists.

Completion and synchronization formats include:
- Classic and ISP24xx status entries.
- Status continuation entries for extra sense data.
- Marker entries and ISP24xx marker entries.
- Completion status constants such as complete, incomplete, DMA error, reset, aborted, timeout, underrun, queue full, port unavailable/logged out/busy, and driver-defined status values.

Management and fabric/control IOCBs include:
- Management Server and CT passthrough entries.
- ELS passthrough request and response entries.
- Task management entries.
- Abort command entries.
- Login/logout/log entry structures.
- Virtual port control, virtual port modify, and report-ID acquisition entries.
- Menlo firmware verification and Menlo data access entries.

Target-mode and IP-over-FC layouts include:
- Enable/modify LUN entries.
- Immediate notify and notify acknowledge entries, with ISP24xx variants.
- ATIO and CTIO request/response structures.
- IP transmit, receive, receive-continuation, 24xx receive, and buffer pool entries.

The `ql_mbx_iocb_t` union collects the major mailbox-executed IOCB variants into one command container.

## Interfaces

The prototypes exported for `ql_iocb.c` cover:
- Starting IOCBs and issuing markers.
- Loading receive buffers.
- Building command, management-server, and IP IOCBs.
- Separate 24xx builders for command, management-server, and IP IOCBs.

## Integration Notes

This header is layout-sensitive. Most structures mirror firmware queue entries and DMA-visible hardware formats, so field order, width, and padding are part of the driver/firmware ABI. It depends on driver-private types such as `ql_adapter_state_t`, `ql_srb_t`, `ql_request_q_t`, `ql_tgt_t`, and `ql_lun_t` from the broader `qlc` driver.
