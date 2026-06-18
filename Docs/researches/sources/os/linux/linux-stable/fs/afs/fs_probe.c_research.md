# File Research: sources/os/linux/linux-stable/fs/afs/fs_probe.c

## Summary
Implements fileserver endpoint probing. It periodically sends `FS.GetCapabilities` to each known fileserver address, records responsive endpoints, detects YFS/AFS capability differences, updates RTT/preferred address state, and feeds the server rotation logic.

## Main Responsibilities
- Manages reference-counted `struct afs_endpoint_state` probe snapshots.
- Schedules fast and slow probe polling.
- Dispatches probes across all fileserver addresses by address preference.
- Processes probe results, errors, capabilities, RTT, and service upgrade.
- Provides wait helpers for operations needing responsive endpoints.
- Cleans up probe timers during namespace teardown.

## Key APIs
- `afs_fs_probe_fileserver()`.
- `afs_fileserver_probe_result()`.
- `afs_wait_for_fs_probes()`.
- `afs_probe_fileserver()`.
- `afs_fs_probe_dispatcher()`.
- `afs_wait_for_one_fs_probe()`.
- `afs_fs_probe_cleanup()`.

## Important Behavior
Responsive servers are moved to the slow probe list and nonresponsive servers to the fast list. Fast polling is 30 seconds; slow polling is 5 minutes.

Probe results distinguish local failures, unreachable/network failures, responded aborts, and successful replies. A YFS response sets `AFS_SERVER_FL_IS_YFS`; AFS capability word 0 controls `AFS_SERVER_FL_HAS_FS64`.

The best RTT endpoint becomes both `server->rtt` and `alist->preferred`. Responsive and failed endpoint sets are captured in `endpoint_state` so concurrent operation rotation is not disrupted by later probe rounds.

## State and Synchronization
`server->fs_lock` protects installation of new endpoint state. `server->probe_lock` protects probe-result aggregation. `net->fs_lock` protects fast/slow probe queues. Endpoint states are refcounted and freed by RCU.

## Risks
`afs_fs_probe_fileserver()` installs a new endpoint state before probes complete, so consumers must handle superseded states. Timer/work accounting uses `servers_outstanding`; missed decrements would affect namespace teardown waits.
