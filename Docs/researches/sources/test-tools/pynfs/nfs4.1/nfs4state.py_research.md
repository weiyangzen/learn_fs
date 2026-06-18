# sources/test-tools/pynfs/nfs4.1/nfs4state.py

## Purpose
`nfs4state.py` implements the server-side stateid and per-file state model used by `nfs4server.py`. It tracks NFSv4 open share state, byte-range locks, delegations, pNFS layouts, anonymous special stateids, and a data-server stateid bypass hack.

## Important APIs, Types, and Functions
- `find_state(env, stateid, allow_0=True, allow_bypass=False)` is the central context manager for resolving and locking a stateid. It maps special all-zero, all-ones, current, layout, and data-server stateids.
- `ByteLock` models byte ranges and conflict checks.
- `DictTree` is a fixed-depth tree used to store state entries by keys such as `(client, open_owner)` or `(client, open_owner, lock_owner)`.
- `FileStateTyped` is the base for typed state collections and creates unique `other` values for stateids.
- `ShareState`, `ByteState`, `DelegState`, `LayoutState`, and `AnonState` each own one category of state for a file.
- `FileState` aggregates the typed states and exposes methods used by the server: `test_share`, `add_share`, `recall_conflicting_delegations`, `grant_delegation`, `grant_layout`, and lock-owner creation.
- `StateTableEntry` is the base class for concrete entries: `ShareEntry`, `ByteEntry`, `DelegEntry`, `LayoutEntry`, `AnonEntry`, and `DSEntry`.

## Control Flow
Protocol operations call `find_state` with the compound environment's current filehandle and requested `stateid4`. The context manager normalizes special stateids, looks up the owning `StateTableEntry` in the current client's state dictionary, verifies filehandle match and seqid validity, acquires the shared file-state lock, yields the entry, and releases the lock.

OPEN uses `ShareState.add_share` through `FileState.add_share`, which first tests current share conflicts. LOCK creates or uses a `ByteEntry`, then `ByteEntry.add_lock` tests conflicting locks and records the range. Delegation grant uses `DelegState.grant_delegation`; conflicting opens use `DelegState.recall_conflicting_delegations`, which starts callback recall threads and raises `NFS4ERR_DELAY`. Layout grant uses `LayoutState.grant_layout` to ask the file object for a layout and populate a `LayoutEntry`.

## State and Persistence Behavior
All state is in memory and tied to file objects plus client records. Each server-issued stateid uses a client-unique `other` value that also indexes `client.state`. Entry deletion marks `invalid` and removes both the file-state tree entry and client-state reference. Anonymous stateids are per-file singleton entries. Data-server mode maps all stateids to a `DS_MAGIC` anonymous entry, intentionally bypassing normal validation.

Read/write activity counters on `StateTableEntry` let state deletion wait for current I/O. Share conflict checks cache aggregate access/deny bits until share state changes.

## Dependencies and Integration Points
The module depends on `locking.Lock`, generated NFSv4 constants/types, `nfs4lib.inc_u32`, `NFS4Error`, `nfs_ops.NFS4ops`, and callback transport exposed by the dispatcher/server. It is integrated into file objects through `file.state` and into clients through `client.state`.

## Risks and Edge Cases
Several paths are incomplete or fragile. `FileState.close` references `client` without receiving it, and commented-out lock removal helpers are still referenced in comments. `ByteState.find_conflicts.match` returns after the first key comparison, which may not implement the intended tuple-template matching. `ByteEntry.remove_lock` depends on list equality for `ByteLock`, but only `__cmp__` is defined, making Python 3 behavior risky. `mark_done_writing` checks `write_count + write_count` instead of read plus write count. Delegation and layout recall tracking is skeletal.

The module deliberately ignores DS stateids in data-server mode. That is useful for tests but weakens protocol validation.

## Test Signals
State behavior is tested indirectly by `st_current_stateid.py`, `st_block.py`, `st_delegation.py`, `st_callback.py`, `st_courtesy.py`, and lock/open tests elsewhere in the suite. Key expected signals include `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_OPENMODE`, `NFS4ERR_DENIED`, `NFS4ERR_DELAY`, delegation callback activity, and layout stateid seqid changes.
