<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.c -->
# sources/user-network-fs/samba/source3/lib/util_procid.c

## Purpose
`util_procid.c` converts between OS PIDs and Samba `server_id` process identifiers, including cluster virtual node number state.

## Important APIs, types, and functions
Public functions are `procid_to_pid`, `set_my_vnn`, `get_my_vnn`, `pid_to_procid`, `procid_valid`, and `procid_is_local`. Static global `my_vnn` defaults to `NONCLUSTER_VNN`.

## Control flow
`pid_to_procid` asks messaging datagram code for a per-process unique ID, logs on failure, and returns a `server_id` with pid, unique ID, and current VNN. Locality compares a server ID's VNN with `my_vnn`.

## State and persistence behavior
The only local state is process-global `my_vnn`. Unique IDs come from the messaging datagram subsystem.

## Dependencies and integration points
It depends on `server_id` generated headers, debug logging, and messaging datagram unique-id helpers. It is used by messaging, locking, and process tracking code.

## Risks and edge cases
`procid_valid` only checks for pid not equal to `(uint64_t)-1`; it does not verify process liveness. If unique-id lookup fails, the returned ID has zero unique ID and may be less collision-resistant.

## Test signals
Tests should cover VNN set/get, local versus remote IDs, invalid sentinel PID, pid extraction, and behavior when unique ID lookup fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.c -->
