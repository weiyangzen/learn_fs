# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/loop.h

This OFED-derived RDSv3 loopback transport header declares loop transport state.

Core definitions:
- Extern `rdsv3_loop_transport` exposes the loopback transport operations vector.
- `rdsv3_loop_exit()` tears down loopback transport state.

Risk-sensitive invariants:
- Loopback transport must integrate with generic RDSv3 transport registration and socket receive paths.
- Loopback can pass messages directly back into receive logic, as described by the message structure comments in `rdsv3.h`.
