# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ep.h

This legacy RDS-over-IB endpoint/session header defines the RC endpoint model, session state machine, QP accounting, and endpoint/session APIs.

Core definitions:
- Endpoint types distinguish control and data RC channels.
- Endpoint states cover unconnected, active/passive pending, connected, closing, closed, and error.
- Session states cover created, failed, init, connected, HCA closing, error, active/passive closing, closed, fini, and destroy.
- `RDS_SESSION_TRANSITION` changes session state under writer lock.
- `rds_qp_t` tracks queue-pair depth, level, low-water mark, and pending refill task state.
- `rds_ep_t` contains endpoint identity, HCA/send memory registration info, endpoint lock/state, IB channel/CQ handles, send/receive pools, receive QP state, segmentation tracking, failover buffer IDs, and RDMA ACK memory.
- `rds_session_t` owns active/passive identity, remote/local IP/GIDs, lock/state, data/control endpoints, failover flag, local/remote port maps, and path info.

API surface:
- Session create/init/reinit/open/close/lookup/recycle/fini paths.
- Endpoint RC channel allocation/free, posting receives, polling send completions.
- RC channel open/close, message receive/control handling, send-error handling, and service-console path lookup.

Risk-sensitive invariants:
- Session list membership is protected by global session lock; per-session state by `session_lock`.
- Local and remote port maps are separate congestion/stall bitmaps.
- Failover uses endpoint last-local/remote-buffer IDs and ACK memory fields.
