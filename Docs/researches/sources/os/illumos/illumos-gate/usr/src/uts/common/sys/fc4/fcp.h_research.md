# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcp.h

## Role

`fcp.h` defines Fibre Channel Protocol frame payloads for carrying SCSI commands, data, transfer-ready, and responses over FC.

## Command And Response Payloads

- Defines frame categories `FCP_SCSI_DATA`, `FCP_SCSI_CMD`, `FCP_SCSI_RSP`, and `FCP_SCSI_XFER_RDY`.
- `fcp_cntl_t` encodes tagged-queueing type, task management flags, and read/write data direction bits.
- Defines FCP queue types: simple, head-of-queue, ordered, ACA, and untagged.
- `fcp_ent_addr_t` provides four 16-bit entity-address layers.
- Defines `FCP_CDB_SIZE` 16 and `FCP_LUN_SIZE` 8.
- `fcp_cmd_t` combines entity address, control, 16-byte SCSI CDB, and data length.
- `fcp_status_t` encodes residual under/over, sense-length present, response-length present, and SCSI status.
- `fcp_rsp_t` includes status, residual, sense length, and response length, followed by variable response and sense data.
- Defines `FCP_MAX_RSP_IU_SIZE`.

## PRLI And Transfer Ready

- `struct fcp_rsp_info` and response codes describe no failure, data length mismatch, invalid command, data RO mismatch, unsupported task management, and task management failure.
- `fcp_xfer_rdy_t` carries sequence offset and burst length.
- `fcp_prli` and `fcp_prli_acc` define process login/accept service parameter bitfields including initiator/target functions, image pair, overlay, mixed command/data, and xfer-rdy-disable flags.
