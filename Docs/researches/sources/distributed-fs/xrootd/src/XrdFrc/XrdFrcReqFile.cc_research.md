# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.cc

## Purpose

This file implements the persistent request-file queue used by FRM agents and consumers. It stores fixed-size `XrdFrcRequest` records in a file with a small header, supports append, cancellation, pop, listing, recovery/compaction, and cross-process file locking.

## Important APIs, Types, and Functions

Public methods are `Add()`, `Can()`, `Del()`, `Get()`, `Init()`, `List()`, and `ListL()`. Private helpers include `FileLock()`, `reqRead()`, `reqWrite()`, `ReWrite()`, and failure logging helpers.

`FileHdr` stores offsets for first, last, and free-chain records. `recEnt` is an in-memory recovery list node. `rqMonitor` serializes in-process agent access with a static mutex, while `FileLock()` uses a `.lock` file and `fcntl` locks for interprocess serialization.

## Control Flow

`Init()` opens/locks the lock file, opens/creates the request file, initializes a new file when shorter than one request record, or, for consumer mode, reads all valid records, sorts normal requests by `addTOD`, places registration requests at the front, rewrites a compacted queue file, and references recovered instance names in `CID`.

`Add()` locks the file, obtains either a free-chain slot or appends at EOF, links the new record to the tail unless it is a registration request, writes the record and header, and unlocks. `Can()` scans all records and clears matching request ids by setting empty LFN. `Get()` pops the first valid request, skipping empty canceled records and adding them to the free chain. `Del()` places a known record offset onto the free chain. `List()` scans fixed-size records with a shared lock and formats requested items with `ListL()`.

## State and Persistence Behavior

The request file persists a header at offset zero and fixed-size request records after it. Deleted/canceled entries are represented by empty LFNs and/or free-chain links. Writes update the header and fsync by default. `ReWrite()` compacts through a `.new` file and rename. Agent mode opens/closes the request file around locks; consumer mode keeps it open.

## Dependencies and Integration Points

The implementation depends on `XrdFrcRequest`, `XrdFrcCID`, XrdFrc tracing, XrdSys file/error/platform wrappers, POSIX `pread/pwrite/fcntl/fsync/rename`, and `XrdFrcReqAgent`.

## Risks and Edge Cases

`reqRead()` treats short reads as success because it only checks `rc < 0`. `Can()` clears matching records without repairing linked-list pointers, leaving canceled entries for `Get()` to skip later. `FileLock(lkNone)` closes `reqFD` in agent mode, so callers must not use stale descriptors after unlock. Fixed-size binary record layout is ABI-sensitive.

## Test Signals

Tests should cover new-file initialization, append order, registration FIFO/front behavior, free-chain reuse, cancellation by id, pop semantics and return codes, listing item formats, recovery sorting/compaction, lock behavior across processes, short read/write failures, and fsync/rename failure handling.
