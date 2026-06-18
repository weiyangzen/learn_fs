# File Research: sources/os/linux/linux/fs/ceph/strings.c

Small stringification helper file for CephFS debug/log output.

Exports constant string mappings for:
- MDS states: `ceph_mds_state_name()`
- Session operations: `ceph_session_op_name()`
- MDS operations: `ceph_mds_op_name()`
- Capability operations: `ceph_cap_op_name()`
- Lease operations: `ceph_lease_op_name()`
- Snapshot operations: `ceph_snap_op_name()`

Behavior:
- Each helper switches on protocol enum/constant values and returns a stable lowercase string.
- Unknown values return `"???"`.
- Used by trace/debug paths rather than core protocol mutation.

Notable detail:
- `CEPH_MDS_OP_SETLAYOUT` maps to `"setlayou"` in this source, missing the final `t`.
