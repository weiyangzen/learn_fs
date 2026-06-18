# sources/test-tools/pynfs/nfs4.0/servertests/st_replay.py

Purpose: Tests duplicate request cache/replay behavior by sending repeated compounds with the same XID for stateful and non-stateful operations including `OPEN`, failed opens/lookups, `LOCK`, denied locks, `LOCKU`, `CLOSE`, `OPEN_CONFIRM`, and directory `CREATE`.

Important APIs/types/functions: `_replay(env, c, ops, error=NFS4_OK)` captures `c.xid`, temporarily overrides `c.get_new_xid`, sleeps between repeats, and checks that replayed calls return the same status. Tests use XDR types such as `exist_lock_owner4`, `locker4`, `createtype4`, and operations from `nfs_ops`.

Control flow: Each public test builds an operation list, calls `_replay`, and relies on duplicate XID reuse to trigger server replay cache behavior. Some tests first create locks/open state and then replay a conflicting or cleanup operation.

State and persistence behavior: Mutates open, lock, close, and create state and exercises server duplicate request cache persistence. Timed variants sleep past the lease before replaying.

Dependencies and integration points: Relies on pynfs client internals (`xid`, `get_new_xid`) and server DRC timing. Comments note Linux may drop too-fast replays and that this imitates a buggy client.

Risks: Replay semantics are transport/server-implementation sensitive and can be flaky. Overriding XID generation can disturb later client sequence expectations if not restored; the helper uses `finally`.

Test signals: Expects stable replay of `NFS4_OK`, `NFS4ERR_NOENT`, `NFS4ERR_ISDIR`, `NFS4ERR_DENIED`, `NFS4ERR_EXPIRED`, and `NFS4ERR_BAD_SEQID` depending on the original call.
