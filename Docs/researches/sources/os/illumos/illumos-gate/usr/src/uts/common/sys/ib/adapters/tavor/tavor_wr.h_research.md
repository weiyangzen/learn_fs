# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_wr.h

## Purpose

Defines work request and WRID tracking support for Tavor QP/SRQ posting and completion processing, including WQE address macros, special-QP MAD helpers, WRID list/work queue structures, lock ordering, and posting/WRID function prototypes.

## Main Definitions

- `TAVOR_QP_WQEADDRSZ()` packs a WQE address and size into the CQE-compatible WRID tracking value.
- `TAVOR_QP_SQ_ENTRY()`, `TAVOR_QP_RQ_ENTRY()`, and `TAVOR_SRQ_WQ_ENTRY()` compute WQE addresses from queue base and tail index.
- `TAVOR_SRQ_WQE_INDEX()` and `TAVOR_SRQ_WQE_ADDR()` convert between SRQ WQE address and index.
- Directed-route MAD helper macros extract management class, hop pointer, and hop count from fragmented buffers and adjust hop pointer for management class `0x81`.
- `struct tavor_wrid_entry_s`: stores application WRID, packed WQE address/size, and signaled/doorbelled flags.
- `tavor_sw_wqe_dbinfo_t`: returns doorbell opcode/fence information from WQE builders.
- `struct tavor_wq_lock_s`: refcounted mutex shared by work queues and SRQs for WRID list manipulation.
- `struct tavor_wrid_list_hdr_s`: WRID queue/list state, including active/retired lists and SRQ-specific buffer metadata.
- `struct tavor_workq_hdr_s`: CQ-associated work queue tracking header keyed by QPN and queue type.
- Lock annotations define ordering: CQ lock, CQ WRID header lock, then WQ lock.
- Queue type constants for receive, send, and SRQ.
- Prototypes for posting send/receive/SRQ WRs and for WRID reset handling, add/get operations, WRID list allocation, SRQ WRID init, CQ reap/force reap, WQ lock refcounts, and SRQ CQE matching.

## Integration Notes

This header links the QP/SRQ posting path to completion processing. Work queue headers live with CQs rather than QPs so completions can still be resolved after a QP is reset or destroyed.

## Risks and Gotchas

- WRID lists can outlive the active QP incarnation; reset and reap paths must avoid mixing old and new queue state.
- Special-QP directed-route MAD macros assume exact packet offsets.
- The packed address/size value depends on `TAVOR_WQE_NDS_MASK`, defined elsewhere, and must match CQE hardware encoding.
- Lock order is explicitly documented and should not be inverted in posting/completion/reset code.
