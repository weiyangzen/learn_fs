# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_queue.h

## Purpose

Defines SLI4 queue entry formats, WQE overlays, queue sizing constants, and doorbell register layouts for the `emlxs` driver.

## Main Definitions

### Completion and Event Entries

- `EQE_t` / `EQE_u`: event queue entry with valid bit, major/minor code, and CQ id.
- CQE types:
  - `CQE_CmplWQ_t`
  - `CQE_RelWQ_t`
  - `CQE_UnsolRcv_t`
  - `CQE_UnsolRcvV1_t`
  - `CQE_XRI_Abort_t`
  - `CQE_ASYNC_t`
  - `CQE_MBOX_t`
- `CQE_u`: union over raw words and all CQE interpretations.
- Defines CQE type codes for WQ completion, release WQE, unsolicited receive, XRI aborted, and unsolicited receive V1.

### Async Event Details

Defines async FCoE, link-state, QoS, FC link attention, and port event payloads, plus constants for topology, attention type, shared link status, port fault, physical speed, event codes, FC link events, FIP events, group 5 events, and port events.

### RQ and WQE Formats

- `RQE_t`: receive queue DMA address entry.
- WQE command overlays:
  - `ELS_REQ_WQE`
  - `ELS_RSP_WQE`
  - `GEN_REQ_WQE`
  - `XMIT_SEQ_WQE`
  - `FCP_WQE`
  - `ABORT_WQE`
  - `BLS_WQE`
  - `CREATE_XRI_WQE`
- `emlxs_wqe_t`: full SLI4 WQE with command-specific first six words, context/XRI tags, timer/class/command fields, abort/request tags, CCP/performance/length/control flags, completion queue id, command type, command-specific word, and first data BDE.

Defines command type constants for FCP data in/out, target receive/response/send, generic, abort, ELS, and FIP mask. Defines ELS id constants for PLOGI/FLOGI/FDISC/LOGO/CMD.

### Queue Sizes

Defines receive buffer sizes/counts, WQE/CQE sizes, EQ/CQ/WQ/MQ/RQ depths, and max WQs per EQ.

### Doorbells

Defines packed doorbell layouts and raw-word unions for:

- `emlxs_rqdb_t` / `emlxs_rqdbu_t`
- `emlxs_wqdb_t` / `emlxs_wqdbu_t`
- `emlxs_cqdb_t`, `emlxs_cqdb6_t`, `emlxs_cqdb_u`
- `emlxs_eqdb_t`, `emlxs_eqdb6_t`, `emlxs_eqdb_u`
- `emlxs_mqdb_t` / `emlxs_mqdbu_t`

## Integration Notes

This header supplies the SLI4 data-plane queue ABI used by IOCB wrappers, mailbox queue creation, interrupt/completion processing, receive buffer posting, and work queue submission.

It depends on `ULP_BDE64` and endian macros supplied by other driver headers.

## Risks and Gotchas

- Like the mailbox and IOCB headers, this file is highly endian-sensitive.
- `WQE_PHWQ_WQID` writes into a WQE via a `uint16_t *` cast at fixed offsets. That is intentionally layout-coupled and fragile.
- Queue depth macros assume page size and element size relationships; changes must stay aligned with mailbox queue creation contexts.
- Doorbell bitfield layouts differ by interface type (`if_type 0,2` versus `if_type 6`) for CQ/EQ.
