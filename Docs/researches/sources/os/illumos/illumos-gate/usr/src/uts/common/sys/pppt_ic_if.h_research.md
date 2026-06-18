# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pppt_ic_if.h

## Purpose
Defines the STMF/PPPT ALUA interconnect messaging API, including message types, payload layouts, allocator functions, free/transmit hooks, and receive entry points.

## Main Interfaces
- Message types:
  - proxy port register/deregister
  - LUN register/deregister/active
  - SCSI command/data/data-done/status/R2T
  - generic status
  - session create/destroy
  - echo request/reply
- `stmf_ic_msgid_t`: 64-bit message identifier.
- `stmf_ic_msg_t`: generic message container with type, ID, optional nvlist, and typed message pointer.
- Message payload structs:
  - `stmf_ic_reg_port_msg_t`
  - `stmf_ic_dereg_port_msg_t`
  - `stmf_ic_reg_dereg_lun_msg_t`
  - `stmf_ic_scsi_cmd_msg_t`
  - `stmf_ic_scsi_data_msg_t`
  - `stmf_ic_scsi_data_xfer_done_msg_t`
  - `stmf_ic_scsi_status_msg_t`
  - `stmf_ic_r2t_msg_t`
  - `stmf_ic_status_msg_t`
  - `stmf_ic_session_create_destroy_msg_t`
  - `stmf_ic_echo_request_reply_msg_t`
- Message status:
  - `STMF_IC_MSG_SUCCESS`
  - `STMF_IC_MSG_IC_DOWN`
  - `STMF_IC_MSG_TIMED_OUT`
  - `STMF_IC_MSG_INTERNAL_ERROR`
- Allocator typedefs and functions for register/deregister port, register/deregister/active LUN, SCSI command/data/data-done/status/R2T, status, session create/destroy, and echo messages.
- Message lifecycle/transport:
  - `stmf_ic_ioctl_cmd()`
  - `stmf_ic_msg_free()`
  - `stmf_ic_tx_msg()`
  - `stmf_ic_rx_msg()`
  - `stmf_msg_rx()`

## Dependencies And Relationships
Includes `sys/stmf_defines.h` and uses STMF SCSI task/session/port/status types, SCSI device descriptors, remote port data, and nvlists. Function typedefs support dynamic symbol import via `ddi_modsym()`.

## Research Notes
The generic message may share string/array storage with its backing nvlist after unmarshalling; callers must keep the nvlist alive while using such fields. `stmf_ic_tx_msg()` frees messages after sending.
