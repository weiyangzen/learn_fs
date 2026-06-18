# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_qp.h

## Purpose
Defines Queue Pair defaults, QP number masks, scheduling helpers, service-type validation, WQ sizing types, QP range/QPN tracking, software QP handle state, and QP allocation/modification prototypes.

## Main Interfaces
- Defaults:
  - `HERMON_NUM_QP_SHIFT`
  - `HERMON_NUM_QPS`
  - `HERMON_QP_MIN_SIZE`
  - `HERMON_LOG_NUM_RDB_PER_QP`
  - `HERMON_NUM_SGL_PER_WQE`
  - `HERMON_QP_ACKREQ_FREQ`
  - `HERMON_QP_LOG_MAX_MSGSZ`
- QP masks:
  - `HERMON_QP_MAXNUMBER_MSK`
  - `HERMON_QP_XRC_MSK`
- Special QP and scheduling:
  - `HERMON_QP_SMI`, `HERMON_QP_GSI`
  - default scheduling policy/selection constants.
  - `HERMON_QP_SCHEDQ_GET()`
- `HERMON_QP_TYPE_VALID()` maps IBT transport types to Hermon service types, including FCoIB-related UD services.
- `hermon_qp_wq_type_t`: send/receive/MLX WQ type classification for WQE sizing.
- `hermon_qp_range_t`: resource range with refcount for RSS/FEXCH QPs.
- `hermon_qp_info_t`: allocation input/output carrier.
- `hermon_qpn_entry_t`: AVL-tracked QPN reservation/refcount entry.
- `struct hermon_sw_qp_s`: complete software QP handle with locks, state/type/QPN, PD/MR/CQ handles, special-QP info, UAR/user mapping state, send and receive work queue metadata, doorbell record, resources, handler argument, SQD event flags, SRQ, multicast refcount, saved MTU, QPN handle, queue allocation info, FCoIB attributes, QP range, and cached hardware QPC.
- `HERMON_SET_QP_POST_SEND_STATE()` updates the cached post-send state under the SQ lock.
- Prototypes cover normal/special/range QP allocation, free, query, lookup, QPN release/AVL init/fini, modify, and reset.

## Dependencies And Relationships
Software QP state embeds `struct hermon_hw_qpc_s` from `hermon_hw.h`, uses CQ/MR/PD/SRQ handles, and drives command opmasks from `hermon_cmd.h`. Work request posting code uses the send/receive queue metadata and state cache.

## Research Notes
The QP handle is the densest software handle in this group. Its annotations distinguish immutable setup data, QP-lock state, SQ-lock post-send state, and fields protected by broader sharing schemes.
