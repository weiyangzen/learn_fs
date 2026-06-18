# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStats.hh

## Purpose
`XrdSsiStats.hh` declares the SSI statistics collector. It extends `XrdOucStats` and exposes counters that track SSI request bytes, response types, callback counts, errors, resource changes, and lifecycle events.

## Important APIs and Types
The public fields are the counters updated by SSI request/response code. `setFS(XrdSfsFileSystem*)` configures a chained filesystem stats provider. `Stats(char *, int)` formats the counters. The private state is only `fsP`; locking is inherited through `XrdOucStats`.

## Control Flow
Other SSI components increment public counters directly, and `XrdSsiSfs::getStats` asks this object to serialize them.

## State and Persistence
Counters live in memory and reset on process start. No persistence or periodic flushing exists in this class.

## Dependencies and Integration Points
It depends on `XrdSysPthread.hh`, `XrdOucStats.hh`, and forward declarations for `XrdSfsFileSystem` and `XrdStats`. The global instance is defined in `XrdSsiStats.cc`.

## Risks and Test Signals
Public mutable counters can be incremented without consistent locking if callers are careless. Tests should cover constructor zeroing, stats serialization after increments, native filesystem stats inclusion, and concurrent updates during formatting.
