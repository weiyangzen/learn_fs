<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.h -->
# sources/user-network-fs/samba/source3/lib/util_procid.h

## Purpose
This header declares Samba process-ID conversion helpers.

## Important APIs, types, and functions
It includes `server_id.h` and declares PID/VNN conversion and predicate functions.

## Control flow
Callers convert PIDs to `server_id` before interacting with messaging/locking subsystems and test validity/locality as needed.

## State and persistence behavior
The header has no state. Implementation maintains process-global VNN.

## Dependencies and integration points
It exposes source3 process identity to code that should not directly know the implementation's VNN storage.

## Risks and edge cases
Callers should not equate `procid_valid` with live process checks.

## Test signals
Compile coverage plus functional tests in `util_procid.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_procid.h -->
