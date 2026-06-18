# File Research: sources/os/linux/linux/fs/afs/fs_probe.c

## Purpose
Maintains fileserver endpoint probing, capability detection, responsiveness tracking, and periodic probe scheduling.

## Main Responsibilities
- Creates and publishes `afs_endpoint_state` records for each probe generation.
- Sends asynchronous `FS.GetCapabilities` probes to all known fileserver addresses.
- Records responsive and failed endpoints, RTT, YFS upgrade status, and FS64 capability.
- Provides wait helpers for operations that need responsive server endpoints.
- Runs fast/slow periodic probe queues to keep routing and NAT state fresh.

## Key Functions and Data
- `afs_fs_probe_fileserver()` builds a fresh endpoint state, assigns the address list, and probes each address by priority.
- `afs_fileserver_probe_result()` consumes call results and updates endpoint/server flags, RTT, preferred address, and failure masks.
- `afs_wait_for_fs_probes()` waits for one untried responsive endpoint, supersession, completion, or interrupt.
- `afs_wait_for_one_fs_probe()` waits up to two seconds for a specific server probe.
- `afs_fs_probe_dispatcher()` processes fast and slow probe queues and re-arms timers.
- `afs_probe_fileserver()` triggers immediate probing when rotation has exhausted addresses.

## Important Details
- Responding servers move to the slow queue; nonresponding servers move to the fast queue.
- AFS capability word 0 is used to set or clear `AFS_SERVER_FL_HAS_FS64`.
- YFS response upgrades set `AFS_ESTATE_IS_YFS` and `AFS_SERVER_FL_IS_YFS`.
- Old endpoint states are marked `AFS_ESTATE_SUPERSEDED` so waiters can restart against newer probe data.
