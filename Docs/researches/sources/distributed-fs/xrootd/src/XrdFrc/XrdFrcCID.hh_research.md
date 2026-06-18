# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.hh

## Purpose

This header declares `XrdFrcCID`, the File Residency Manager cluster-id registry, and the global `XrdFrc::CID` instance.

## Important APIs, Types, and Functions

Public methods add cluster identity records, retrieve cluster names into buffers or `XrdOucEnv`, initialize from a queue path, and mark instance names referenced. Private `cidEnt` nodes hold identity data and `cidMon` serializes access with a static `XrdSysMutex`.

## Control Flow

Callers initialize the registry from a checkpoint directory, then add registrations as FRM clients appear and query cluster names when composing request environment or recovering queue state.

## State and Persistence Behavior

The class stores a linked list, default entry pointer, and checkpoint filenames. The source implementation persists to `CIDS` files under the queue path.

## Dependencies and Integration Points

It depends on XrdSys pthread mutex wrappers and forward-declares `XrdOucEnv`/`XrdOucStream`. It is used by request-file recovery and FRM registration paths.

## Risks and Edge Cases

The destructor does not free linked-list entries or filename strings, so the object is effectively process-lifetime. Copy/move operations are not explicitly disabled. The registry exposes raw C-string buffers for callers to size correctly.

## Test Signals

Header-level tests should cover inclusion and API use with forward declarations. Behavior tests live in the source implementation.
