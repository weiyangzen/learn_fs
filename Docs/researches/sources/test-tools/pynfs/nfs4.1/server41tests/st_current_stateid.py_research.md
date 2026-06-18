# sources/test-tools/pynfs/nfs4.1/server41tests/st_current_stateid.py

## Purpose
`st_current_stateid.py` tests NFSv4.1 current-stateid processing, where `stateid4(seqid=1, other=all-zero)` refers to the current stateid produced by prior operations in the same compound.

## Important APIs, Types, and Functions
- `current_stateid = stateid4(1, b'\0' * 12)` is the test's current-stateid marker.
- Tests cover OPEN+CLOSE, LOCK+LOCKU, OPEN+WRITE+CLOSE, LOCK+WRITE+LOCKU, current stateid invalidation after filehandle changes, close without prior stateid, OPEN+LAYOUTGET, OPEN+SETATTR, FREE_STATEID interactions, and SAVEFH/RESTOREFH preservation.

## Control Flow
Tests build multi-op compounds where an operation that returns a stateid is followed by an operation that consumes `current_stateid`. Negative tests change the current filehandle with LOOKUP or omit a stateid-producing op and expect stale/bad stateid errors.

## State and Persistence Behavior
The file exercises compound-local state tracking in the client/server response flow, not durable state. It also touches open, lock, layout, setattr, and free-stateid server state.

## Dependencies and Integration Points
It depends on helpers from `environment.py`, generated open/lock types, `nfs_ops`, and pNFS support for the layout test.

## Risks and Edge Cases
Current-stateid semantics are sensitive to current filehandle changes and to which operation last produced state. Tests expect either `NFS4ERR_STALE_STATEID` or `NFS4ERR_BAD_STATEID` in some negative paths, allowing implementation variation.

## Test Signals
Positive signals are `NFS4_OK` for valid same-compound current-stateid consumers. Negative signals include stale or bad stateid errors after unrelated LOOKUP or when no usable current stateid exists, and `NFS4ERR_LOCKS_HELD` for FREE_STATEID plus CLOSE sequencing.
