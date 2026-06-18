# File Research: sources/virtualization/libguestfs/lib/launch.c

Generic launch orchestration and backend registry.

Important behavior:
- `guestfs_impl_launch` validates CONFIG state, checks backend max disks when available, creates tmpdir lazily, logs launch diagnostics, then delegates to `g->backend_ops->launch`.
- Launch progress is approximate and emitted after five seconds through `guestfs_int_launch_send_progress`.
- Provides state queries: config, launching, ready, busy compatibility, and raw state.
- `guestfs_impl_config` appends extra hypervisor parameters while rejecting parameters that would conflict with libguestfs-managed kernel, display, serial, and graphics options.
- Backend registration uses a global linked list populated by backend constructor functions.
- `guestfs_int_set_backend` resolves backend names and `backend:arg` strings, maps legacy `appliance` to `direct`, installs backend ops, and allocates backend-private data.
- `guestfs_int_passt_runnable` probes `passt --help` and accepts exit status 0 or 1.
- `guestfs_int_force_load_backends` keeps static linking from dropping backend constructors.

Filesystem relevance:
- Controls when appliance-backed filesystem access can start and enforces backend disk-count limits before guest disks are exposed.
