# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/repair.h

## Purpose
Declares the online repair API used by XFS scrub and provides no-op or unsupported stubs when online repair or realtime/quota support is not compiled.

## Major Components
- `xrep_notsupported`: common `-EOPNOTSUPP` stub.
- Repair orchestration declarations: `xrep_attempt`, `xrep_will_attempt`, `xrep_failure`.
- Transaction and reservation declarations.
- `struct xrep_find_ag_btree`: describes per-AG btrees to locate via rmap scanning.
- Setup declarations for AG btrees, inode metadata, directory/xattr/nlink repair, realtime btrees.
- Repair entry point declarations for all scrub types.
- Conditional realtime and quota declarations.
- Stub definitions under `!CONFIG_XFS_ONLINE_REPAIR`.

## Control Flow and Invariants
When online repair is enabled, this header exposes concrete repair helpers and repairers. When disabled:
- `xrep_will_attempt` still returns true for force rebuild or detected repair need so the caller can reach `xrep_attempt`.
- `xrep_attempt` returns `-EOPNOTSUPP`.
- Repair entry points map to `xrep_notsupported`.
- Setup functions mostly become no-ops.

## Dependencies and Integration
Included throughout scrub/repair code to abstract feature availability. It mediates compile-time feature differences for:
- `CONFIG_XFS_ONLINE_REPAIR`
- `CONFIG_XFS_RT`
- `CONFIG_XFS_QUOTA`

## Risk and Edge Cases
The no-repair stubs preserve scrub behavior while reporting unsupported repair rather than silently claiming success. Consumers must still check runtime filesystem feature bits, as many repairers also require rmapbt, realtime groups, exchange-range, or reflink support.
