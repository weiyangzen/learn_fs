# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9excl.c

Implements in-memory timed exclusive-open tracking for Fossil 9P fids.

Key behavior:
- `exclAlloc()` checks for an existing exclusive lock on `(Fsys, qid.path)` and rejects it unless expired.
- New exclusive locks live for five minutes and are attached to the opening fid.
- `exclUpdate()` extends an active lock and detects broken or expired locks.
- `exclFree()` removes and frees a fid's exclusive lock.
- `exclInit()` initializes the global lock.

Important implementation details:
- Expired lock records are marked by clearing `fsys`, then a new lock is allocated.
- Locks are process-local and stored in a global doubly-linked list.

Risks and invariants:
- Timed exclusivity depends on clients continuing I/O to refresh the lock.
- This is not a persistent on-disk lock mechanism.
