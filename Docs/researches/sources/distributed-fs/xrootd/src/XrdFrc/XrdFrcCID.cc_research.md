# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.cc

## Purpose

This file implements `XrdFrcCID`, a checkpointed in-memory map from XRootD instance names to cluster names and associated process metadata. It supports FRM client registration and lets request queues preserve cluster identity across restarts.

## Important APIs, Types, and Functions

The global instance is `XrdFrc::CID`. Public methods are `Add()`, `Get(iName, buff, blen)`, `Get(iName, vName, env)`, `Init(aPath)`, and `Ref(iName)`. Private methods are `Find()`, stream-record `Init()`, and `Update()`.

`cidEnt` stores linked-list pointers, instance name, cluster name, add timestamp, pid, use count, and cached string lengths. `cidMon` wraps a static mutex for all CID operations.

## Control Flow

`Init(aPath)` opens the `CIDS` checkpoint file, reads records of `<iname> <cname> <addt> <pid>`, validates timestamp and pid, clears dead pids, and reconstructs the linked list. `Add()` inserts new entries or updates existing entries only when the incoming timestamp is newer. `Update()` writes live/default/referenced entries to `CIDS.new` under a file lock, removes dead unused non-`anon` entries, then renames the temp file to `CIDS`.

`Get()` returns the matching cluster or default `anon` entry when the instance name is empty. `Ref()` marks an entry as used so request-file recovery can prevent cleanup of known instance names.

## State and Persistence Behavior

State is a process-local linked list plus two checkpoint paths, `CIDS` and `CIDS.new`. Persistence is atomic-by-rename after rewriting the full checkpoint file under `fcntl` write lock. Entries with dead pids and no use count are pruned during updates.

## Dependencies and Integration Points

The implementation depends on XrdFrc tracing, XrdOuc streams/environments, XrdSys errors/file descriptors/platform wrappers, POSIX file locking, `writev()`, and `kill(pid, 0)` for liveness checks. `XrdFrcReqFile::Init()` calls `CID.Ref()` for recovered request instance names.

## Risks and Edge Cases

`Init(aPath)` uses fixed 1024-byte path assembly with `strcpy()`. `Update()` uses static iovec buffers, relying on the outer mutex for thread safety. Persistence failures are logged but `Add()` still mutates memory before `Update()` failures. Dead pid detection treats permission errors as alive.

## Test Signals

Tests should cover checkpoint recovery, newer/older update ordering, default `anon` behavior, environment injection, dead-pid pruning, `Ref()` preservation, corrupt records, and atomic rename failure paths.
