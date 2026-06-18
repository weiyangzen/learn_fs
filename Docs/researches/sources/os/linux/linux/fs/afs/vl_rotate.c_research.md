# File Research: sources/os/linux/linux/fs/afs/vl_rotate.c

## Scope

This file implements VL server cursor initialization, selection, retry/address rotation, final cleanup, and diagnostics for volume-location operations.

## Public And Internal APIs Covered

- `afs_begin_vlserver_operation()` initializes a `struct afs_vl_cursor`.
- `afs_select_vlserver()` iterates over VL servers and addresses.
- `afs_end_vlserver_operation()` releases cursor state and returns the cumulative error.
- Internal `afs_vl_dump_edestaddrreq()` emits debug cursor state on address failures.

## Control Flow And Behavior

- Cursor start checks pending signals, initializes cumulative error to `-EDESTADDRREQ`, and assigns a debug ID.
- VL iteration refreshes DNS data when unavailable or expired, queues cell lookup, waits for initial DNS if needed, handles not-found/unavailable results, and snapshots the current VL server list.
- Selection sends probes for unprobed servers, waits for responsive candidates, prefers the list’s preferred server if still untried, otherwise chooses the lowest RTT responding server.
- For a selected server, it pins the address list and rotates through responded addresses not already tried or probe-failed, favoring the preferred address.
- Previous call results stop on success/local failure, rotate on network failures, rotate server on unsupported service, and retry the whole list once after call reset.
- Address-list preferred index is updated when a non-preferred address successfully responded.
- End cleanup releases pinned address/server lists and dumps state for address-related failures when configured.

## State And Data Structures

- `struct afs_vl_cursor` holds cell, key, server list, selected server, address list, untried bitmask, tried-address bitmask, indices, call result, flags, and cumulative error.
- Uses per-cell DNS status/source/expiry and `vl_servers` RCU pointer.

## Dependencies

- DNS cell lookup machinery, VL server list/probe code, address lists, RxRPC peer addresses, and error prioritization.

## Risks And Invariants

- Only one full-list retry is allowed after retryable reset paths.
- Cursor cleanup must release both address-list and server-list refs on every exit path.
- DNS status loads are ordered after lookup-count changes.
