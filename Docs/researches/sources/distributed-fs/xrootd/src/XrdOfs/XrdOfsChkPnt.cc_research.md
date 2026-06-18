# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsChkPnt.cc

## Purpose

`XrdOfsChkPnt.cc` implements the `XrdOucChkPnt` interface for local OFS files by using `XrdOfsCPFile` to save original data before destructive writes/truncates and to restore the file after cancellation, client failure, close cleanup, or startup recovery.

## Important APIs, Types, and Functions

- `Create()` snapshots the current file size and creates the underlying `XrdOfsCPFile`.
- `Delete()` destroys the checkpoint file if active.
- `Failed()` handles restore failure by chmoding the source file either inaccessible (`000`) or read-only, renaming the checkpoint to error state, logging, and setting `readok`.
- `Query()` reports current checkpoint bytes used and maximum configured size.
- `Restore()` parses checkpoint restore info, opens the source file when running startup recovery, truncates to original size, writes saved data back in reverse order, syncs, restores modification time through `Fctl_utimes`, deletes the checkpoint, and logs success.
- `Truncate()` checkpoints bytes that would be lost by truncating below the original size.
- `Write()` checkpoints original bytes overlapped by one or more write ranges.
- Local RAII `cUp` closes an OSS file pointer, frees temporary buffers, and closes an fd.

## Control Flow

Normal runtime flow is: `Create()` records original file size; each `cpTrunc` or `cpWrite` request calls `Truncate()` or `Write()` before the destructive operation; close or explicit restore calls `Restore()` if needed; `Delete()` removes checkpoint state when the operation commits. Startup recovery constructs `XrdOfsChkPnt` with no `lFN` and a preexisting checkpoint path, then `Restore()` derives the source path from `RestoreInfo()` and opens the file before applying recovery.

`Write()` scans all ranges, marks only ranges overlapping the original file size, reserves space, reads original data from the OSS file, appends those bytes to the checkpoint, and syncs. `Truncate()` uses the same strategy for the tail that would be discarded.

## State and Persistence Behavior

`fSize` is the original/current protected size and is reduced after checkpointing a truncate. `cpUsed` tracks total checkpointed data and is compared with `XrdOfsConfigCP::MaxSZ`. `cpFile` owns the persistent `.ckp` record; successful restore deletes it, while failure renames it to an error state and changes source-file permissions according to `cprErrNA`.

The restore path is conservative: any corruption or write failure leaves the checkpoint in an error state and makes the affected file read-only or inaccessible to avoid silent data loss.

## Dependencies and Integration Points

This file depends on `XrdOssDF` operations (`Fstat`, `Read`, `WriteV`, `Ftruncate`, `Fsync`, `Fctl`, `Open`), global `XrdOfsOss`, global `OfsEroute`, `XrdOfsConfigCP` settings, `XrdOfsCPFile`, and `XrdOucIOVec`. It is instantiated from `XrdOfsFile::CreateCKP()` and from `XrdOfsConfigCP::Recover()`.

## Risks and Edge Cases

- `Write()` appears to compare `dlen + cpUsed` after the loop using the last computed `dlen`, not the sum across all checkpointed ranges; multi-vector quota accounting may undercount. `Reserve(dlen, numVS)` also reserves only that last `dlen`, not total data length.
- `Truncate()` uses `int dlen = fSize - offset`; very large files/truncates could overflow `int` even though `fSize` is `int64_t`.
- `Restore()` calls `Fsync()` but does not check its return value.
- `Failed()` may not be able to chmod or rename, but still returns the original error and logs secondary failures.
- Startup recovery relies on `XrdOfsOss->newFile("checkpoint")`; if that returns null, `Recover()` would dereference null before reaching this class.

## Test Signals

Tests should cover checkpoint create/delete, truncating below and above original size, writes wholly before/after original EOF, multi-range writes, quota enforcement, reserve/read/append/sync failures, restore with no changed data, restore with overlapping changed data, corrupted checkpoint records, startup recovery with `lFN == 0`, and both `cprErrNA` modes.
