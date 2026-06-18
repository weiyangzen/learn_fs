# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.hh

## Purpose

`XrdOfsChkPnt.hh` declares the local OFS checkpoint implementation, `XrdOfsChkPnt`, as a concrete `XrdOucChkPnt` that coordinates a source `XrdOssDF` file and an `XrdOfsCPFile` record.

## Important APIs, Types, and Functions

- Public checkpoint interface: `Create`, `Delete`, `Finished`, `Query`, `Restore`, `Truncate`, and `Write`.
- Constructor accepts an OSS file reference, source LFN, and optional preexisting checkpoint filename. Passing a checkpoint filename is how recovery binds to an existing record.
- `Finished()` deletes `this`, so callers must not use the object after invoking it.
- Private `Failed()` centralizes recovery-failure handling.
- State members are `lFN`, `cpFile`, `ossFile`, `fSize`, and `cpUsed`.

## Control Flow and Contracts

The class is designed for ownership by `XrdOfsFile::myCKP` through the abstract `XrdOucChkPnt` pointer. The caller creates a checkpoint object, calls lifecycle methods, and finally calls `Finished()`. Runtime methods operate on an already-open `ossFile`; recovery mode can be constructed with `lFN == 0` and uses the checkpoint metadata to identify/open the source.

`Truncate()` and `Write()` accept `struct iov` ranges by reference-to-pointer. The implementation writes checkpoint bookkeeping into `range[i].info`, so callers must not treat `info` as immutable across checkpoint calls.

## State and Persistence Behavior

Persistent state is delegated to `XrdOfsCPFile`. `fSize` stores the protected file size used to decide what bytes need checkpointing, and `cpUsed` tracks configured quota consumption. The object itself is heap-lifetime only and self-deletes through `Finished()`.

## Dependencies and Integration Points

The header includes `XrdOfsCPFile.hh` and `XrdOucChkPnt.hh`, forward-declares `iov` and `XrdOssDF`, and is included by `XrdOfs.cc`, `XrdOfsChkPnt.cc`, and `XrdOfsConfigCP.cc`.

## Risks and Edge Cases

- Self-deleting `Finished()` makes ownership simple for callers but dangerous if any caller keeps aliases.
- `lFN` is a raw pointer and can be changed to point inside `XrdOfsCPFile::rInfo` during restore; implementation must not outlive backing restore info in that path.
- The interface does not expose whether a checkpoint is active; callers infer from return codes.
- Range mutation through `info` is implicit in the header contract.

## Test Signals

Tests should verify object lifecycle through `Finished()`, recovery constructor behavior with a preexisting checkpoint filename, query output before and after writes, and that range `info` side effects do not conflict with callers using `struct iov`.
