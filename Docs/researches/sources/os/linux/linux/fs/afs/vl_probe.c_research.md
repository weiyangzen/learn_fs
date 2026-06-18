# File Research: sources/os/linux/linux/fs/afs/vl_probe.c

## Scope

This file probes volume-location servers to determine reachability, RTT, preferred address, and whether the server supports YFS VL service upgrade.

## Public And Internal APIs Covered

- `afs_vlserver_probe_result()` processes completion of one `VL.GetCapabilities` probe.
- `afs_send_vl_probes()` starts probes for unprobed VL servers in a list.
- `afs_wait_for_vl_probes()` waits until an untried server responds or probing finishes.

## Control Flow And Behavior

- A probe run snapshots a server address list, sets `probe_outstanding`, clears previous probe state, and sends async capability calls to each address in priority order.
- Probe completion classifies local errors, network failures, remote aborts, and successful responses.
- Successful or aborted-but-responsive calls mark the address as responded and update YFS/non-YFS capability flags based on returned service ID.
- RTT is read from the RxRPC peer; the lowest RTT becomes server RTT and preferred address.
- When all address probes finish without response, the server is marked nonresponding and RTT becomes `UINT_MAX`.
- `afs_wait_for_vl_probes()` installs waitqueue entries on probing servers, sleeps interruptibly until a response or all probing stops, then chooses the responding untried server with lowest RTT as list preferred.

## State And Data Structures

- Uses `server->probe`, `probe_outstanding`, `probe_wq`, `probe_lock`, `flags`, `rtt`, and address-list `responded`/`probe_failed` bitmaps.
- `struct afs_error` accumulates probe-start errors when no async probe is in progress.

## Dependencies

- Async `afs_vl_get_capabilities()` calls, RxRPC RTT access, address-list refs, VL server flags, wait queues, and error-prioritization helpers.

## Risks And Invariants

- `AFS_VLSERVER_FL_PROBING` is cleared with unlock semantics before waking waiters.
- Probe results must update RTT before setting responded flags.
- A server can respond as YFS or non-YFS; service ID is adjusted accordingly.
