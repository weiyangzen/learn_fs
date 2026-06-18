# File Research: sources/os/linux/linux-stable/fs/afs/vl_probe.c

## Scope

Probes volume-location servers to determine reachability, preferred endpoint, RTT, and YFS service support.

## APIs And Behavior

- `afs_send_vl_probes()` starts `VL.GetCapabilities` probes for unprobed servers.
- `afs_vlserver_probe_result()` records each async probe result, marks responding/failed address bits, stores errors/abort codes, detects YFS via service ID, updates preferred address and RTT, and wakes waiters.
- `afs_wait_for_vl_probes()` waits until an untried server responds or probing finishes/interruption occurs, then picks the lowest-RTT responding server.

## State And Dependencies

Uses per-vlserver `probe`, `probe_outstanding`, flags, waitqueues, address-list `responded`/`probe_failed` bits, and RxRPC smoothed RTT. Probe RPCs are created by `afs_vl_get_capabilities()` in `vlclient.c`.

## Risks And Invariants

Probe completion must clear `PROBING` exactly once when the outstanding count reaches zero. YFS detection changes the server service ID used by later VL calls. Local key/network errors are tracked separately from unreachable endpoint failures.
