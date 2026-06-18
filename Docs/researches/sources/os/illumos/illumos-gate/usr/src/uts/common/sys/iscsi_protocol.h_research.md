# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_protocol.h

This header defines iSCSI protocol wire constants and PDU header structures.

General constants:
- Name/user lengths, listen port 3260.
- 24-bit network-order helpers `ntoh24` and `hton24`.
- Version constants, min/max PDU length, padding length, max key-value pairs.
- Text constants: separator, `None`, `Reject`, `Irrelevant`, `NotUnderstood`.
- Reserved task tag and key/value length constants.
- Final flag and SendTargets strings.

Common headers and opcodes:
- `iscsi_hdr_t` generic template header and `iscsi_rsp_hdr_t`.
- Opcode bits: retry, immediate, opcode mask.
- Client-to-server opcodes: NOP-Out, SCSI command, task management, login, text, data, logout, SNACK.
- Server-to-client opcodes: NOP-In, SCSI response, task management response, login/text response, data response, logout response, R2T, async event, reject.

PDU structures:
- SCSI command/response: `iscsi_scsi_cmd_hdr_t`, `iscsi_scsi_rsp_hdr_t`, `iscsi_addl_hdr_t`.
- Async event: `iscsi_async_evt_hdr_t`.
- NOP: `iscsi_nop_out_hdr_t`, `iscsi_nop_in_hdr_t`.
- Task management: `iscsi_scsi_task_mgt_hdr_t`, `iscsi_scsi_task_mgt_rsp_hdr_t`.
- R2T: `iscsi_rtt_hdr_t`.
- Data: `iscsi_data_hdr_t`, `iscsi_data_rsp_hdr_t`.
- Text: `iscsi_text_hdr_t`, `iscsi_text_rsp_hdr_t`.
- Login: `iscsi_login_hdr_t`, `iscsi_login_rsp_hdr_t`.
- Logout: `iscsi_logout_hdr_t`, `iscsi_logout_rsp_hdr_t`.
- SNACK: `iscsi_snack_hdr_t`.
- Reject: `iscsi_reject_rsp_hdr_t`.

Protocol constants:
- SCSI command flags and command attributes.
- SCSI response flags and status values.
- Async event codes.
- Task management function and response codes, including backward-compatible aliases.
- Data response flags.
- Text continue flag.
- ISID length and login flag helpers `ISCSI_LOGIN_CURRENT_STAGE` and `ISCSI_LOGIN_NEXT_STAGE`.
- Login stages, status classes, and status details.
- Logout reasons and responses.
- SNACK type mask and reject reasons.
- Default, minimum, and maximum operational parameter values.
- IQN/EUI name prefixes and EUI name length.

Dependencies:
- Includes `sys/types.h` and `sys/isa_defs.h`.

Relevance:
- Core iSCSI wire ABI for block storage networking. IDM, initiator, target, authentication, and user ioctl layers all build on these definitions.
