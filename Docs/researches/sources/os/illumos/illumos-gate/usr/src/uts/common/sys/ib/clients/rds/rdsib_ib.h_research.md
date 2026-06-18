# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ib.h

This legacy RDS-over-IB header declares global tunables, HCA state, soft state, and IB initialization/service APIs.

Core definitions:
- Global configuration covers node count, buffer sizes, packet size, send/receive buffer counts, low-water marks, pending RX high-water mark, RNR retry, path retry, and packet lifetime.
- Performance tunables cover interrupt disabling, polling fullness threshold, work-completion signaling, and wait time.
- Loopback port map is a fixed bitmap of 8192 bytes protected by rwlock.
- `rds_hca_t` tracks HCA list state, GUID, port count, IBT handles, PD/MR/lkey/rkey, service-bind handles, attributes, and port info.
- `rds_state_t` is singleton soft state: session list/lock, IB client handle, HCA list/lock, service handle, and service ID.

API surface:
- Service register/bind, receive CQ handler, GID/GUID-to-HCA lookup, IB initialize/deinitialize, and logging lifecycle.

Risk-sensitive invariants:
- HCA state transitions are attach/detach oriented and separate from session state.
- Registered receive-pool memory keys are stored per HCA and used by endpoint receive buffers.
- The driver uses one global soft state rather than per-instance state.
