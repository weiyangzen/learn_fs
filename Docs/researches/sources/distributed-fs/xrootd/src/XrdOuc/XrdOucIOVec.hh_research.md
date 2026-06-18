# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucIOVec.hh

## Purpose
Defines generic file I/O vector structures shared by SFS, OFS, OSS, and checkpoint interfaces.

## Important APIs, Types, And Functions
`XrdOucIOVec` stores file `offset`, byte `size`, arbitrary `info`, and data buffer pointer. `XrdOucIOVec2` is a convenience subclass constructor filling those fields. `struct iov : public XrdOucIOVec` restores an older intended type name while preserving layout compatibility.

## Control Flow
No logic beyond `XrdOucIOVec2` construction. Callers build arrays of these structures and pass them to vector I/O or checkpoint APIs.

## State And Persistence
Each struct is transient parameter state. It does not own the buffer pointer or persist anything.

## Dependencies And Integration Points
No external includes. It is an ABI/layout bridge for old signatures using `struct iov` and newer code using `XrdOucIOVec`.

## Risks And Test Signals
Risks include buffer lifetime/ownership ambiguity, signed `int size` limits for large I/O, and assumptions that subclass layout remains identical to the base. Test signals include compile ABI checks with `sizeof(iov) == sizeof(XrdOucIOVec)`, vector read/write behavior, and checkpoint code using both type names.
