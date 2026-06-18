# File Research: sources/os/linux/linux-stable/fs/afs/vl_rotate.c

## Scope

Implements the VL-server operation cursor and retry/address rotation logic.

## APIs And Behavior

- `afs_begin_vlserver_operation()` initializes a cursor with cell, key, debug ID, and default cumulative error.
- `afs_select_vlserver()` refreshes DNS/VL server lists, sends probes, selects responding VL servers by preferred/lowest RTT, iterates endpoint addresses, updates preferred addresses after responses, and handles retryable transport/op-not-supported errors.
- `afs_end_vlserver_operation()` releases cursor refs, dumps limited debug information for address failures, and returns the prioritized cumulative error.

## State And Dependencies

The cursor owns refs to a VL server list and current address list, tracks untried servers, tried addresses, selected server/address, call result, response state, retry flags, and cumulative error. It depends on DNS cell refresh, VL probes, and `afs_prioritise_error()`.

## Risks And Invariants

The cursor restarts at most once on retry flags to avoid loops. Preferred address updates occur only after a call responded. DNS lookup unavailability or not-found status is translated before any VL RPC is attempted.
