# sources/test-tools/strace/bundled/linux/include/uapi/linux/smc_diag.h

## Purpose

Defines socket diagnostic ABI for SMC-R/SMC-D sockets. strace uses it to decode netlink diagnostic requests and extension attributes that expose SMC connection, link group, fallback, and DMB state.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`, `linux/inet_diag.h`, and `rdma/ib_user_verbs.h`. `struct smc_diag_req` carries family, requested extensions, and `inet_diag_sockid`. `struct smc_diag_msg` is the base response with socket state, mode/fallback field, shutdown, id, uid, and inode. Mode constants distinguish SMC-R, fallback TCP, and SMC-D. Extension ids include `SMC_DIAG_CONNINFO`, `LGRINFO`, `SHUTDOWN`, `DMBINFO`, and `FALLBACK`. Payload structs include `smc_diag_cursor`, `smc_diag_conninfo`, `smc_diag_linkinfo`, `smc_diag_lgrinfo`, `smc_diag_fallback`, and `smcd_diag_dmbinfo`.

## Control Flow, State, and Integration

Netlink diagnostic flow mirrors inet diag: userspace requests SMC sockets and optional extensions, kernel returns base messages and nested attributes. State belongs to live SMC sockets, RDMA links, direct memory buffers, fallback causes, and cursor positions.

## Risks and Test Signals

Risks include treating `diag_fallback` as a boolean when it aliases mode, fixed one-entry link arrays hiding variable netlink nesting, RDMA device-name size dependencies, and 64-bit aligned token/gid fields. Test signals include request/response decoding, extension id names, cursor formatting, fallback reason fields, and SMC-D DMB token output.
