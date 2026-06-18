# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh` defines the transient state block used by XRootD vector-write processing. It is a compact dynamically-sized carrier for decoded `kXR_writev` segments, current file handle grouping, resume indices, sync behavior, and monitoring flags. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

The only exported type is `struct XrdXrootdWVInfo`. Important fields are `wrVec`, a pointer to the embedded `XrdOucIOVec` array; `curFH`, the current grouped file handle; `vBeg`, `vPos`, `vEnd`, and `vMon`, which track vector progress and monitoring boundaries; `doSync`, which requests a file sync after each grouped write; `wvMon`, `ioMon`, and `vType`, which are intended to drive vector-write monitoring; and `ioVec[1]`, the flexible-array-style trailing storage allocated larger than the struct itself.

## Control Flow

This header has no executable flow, but its layout is consumed directly by `XrdXrootdProtocol::do_WriteV()`, `do_WriteVec()`, and checkpoint execution of embedded writev requests. The runtime flow is: allocate enough bytes for `XrdXrootdWVInfo` plus all decoded vector entries, populate the embedded `ioVec`, then advance `vPos` and `vBeg` as socket data is read and grouped `writev` calls are issued.

## State and Persistence Behavior

Instances are per-protocol-request heap allocations stored through `XrdXrootdProtocol::wvInfo`. The state can survive a short protocol resume when socket reads are incomplete, but it is not persistent beyond the connection/request and is freed on completion or error. The flexible-array layout means allocation size and field initialization are part of the contract.

## Dependencies and Integration Points

The only direct include is `XrdOuc/XrdOucIOVec.hh`. Integration is with XRootD protocol execution, SFS file `writev`, checkpointed writev handling, and optional file I/O monitoring. The struct must remain compatible with code that casts and indexes the trailing `ioVec` storage.

## Risks and Edge Cases

Because the struct uses a one-element trailing array rather than standard C++ flexible storage, any allocation-size mistake corrupts memory. The short index fields constrain vector counts to protocol limits and assume `XrdProto::maxWvecsz` remains safely within `short`. Monitoring fields are easy to misinitialize because they carry raw flags rather than a small typed state machine.

## Test Signals

Useful signals include writev tests with one file, multiple file handles, zero-length elements, partial socket reads that force resume, `doSync` enabled, and checkpoint-wrapped writev. Memory sanitizers should cover allocation and freeing paths, and monitoring tests should verify vector and per-segment counters when enabled.
