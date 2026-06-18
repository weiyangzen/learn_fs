# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsCPFile.cc

## Purpose

`XrdOfsCPFile.cc` implements the on-disk checkpoint record format used by `XrdOfsChkPnt`. It creates checkpoint files under the configured checkpoint path, stores the source logical filename in both an xattr and a CRC-protected header, appends CRC-protected original-data segments, reserves space before mutation, validates/restores metadata for recovery, and destroys or renames checkpoint files after success or failure.

## Important APIs, Types, and Functions

- Local `cpHdr` is the checkpoint header: CRC32C, header length, source-LFN length, original file size, original mtime, reserved fields, and `" file://"` marker followed by the source LFN.
- Local `cpSeg` is an appended data segment: CRC32C, data length, and original file offset followed by the original bytes.
- `XrdOfsCPFile::Create()` generates a unique `.ckp` path, creates it exclusively, stores xattr `xrdckp_srclfn`, writes a CRC-protected header, and fsyncs it.
- `Append()` writes a segment header plus data via `writev()`, maintaining `ckpDLen` and `ckpSize`.
- `Reserve()` uses `posix_fallocate()` or Darwin `F_PREALLOCATE`, truncating back on failure.
- `RestoreInfo()` opens the checkpoint, reads it whole, validates header and segment CRCs, extracts source filename/size/mtime, builds restore vectors in reverse order, and reports corruption causes.
- `Destroy()` tries `unlink()`, falling back to truncate plus `ErrState()` when unlink fails.
- `ErrState()` renames the checkpoint by appending `err` to leave a failure trail.
- `Target()` recovers the source filename from xattr first, then from the header.
- Static `genCkpPath()` uses a process-time hex prefix and mutex-protected sequence number to build names beneath `XrdOfsConfigCP::Path`.

## Control Flow

Create begins by rejecting an already-active object, generating a path, opening it with `O_CREAT|O_EXCL|O_WRONLY`, setting xattr metadata, then writing and syncing the header. Append is intentionally append-only: callers reserve space first, then append original data segments, then call `Sync()`.

Restore reads the full checkpoint into memory and validates before exposing any restore vector. Segment iteration stops either at a zero-filled allocated tail marker or at EOF. Accepted segments are returned in reverse order so later writes are restored first, preventing overlapping writes from corrupting earlier original data.

## State and Persistence Behavior

The persistent file layout is self-validating through CRC32C over the header excluding its CRC field and each segment excluding its CRC field plus data. The xattr is a fast source-name lookup and a fallback when the header or open path fails. Zero-length checkpoints mean the checkpoint was not committed and should be ignored by the restore layer.

In-memory state is `ckpFN`, `ckpFD`, `ckpDLen`, and `ckpSize`. The destructor closes the fd and frees the filename; it does not delete the checkpoint file. Deletion is explicit through `Destroy()` so crash recovery can find outstanding records.

## Dependencies and Integration Points

This file depends on `XrdOfsConfigCP::Path`, native xattrs through `XrdSysXAttrNative`, `XrdOucCRC` for CRC32C, `XrdOucIOVec` for restore vectors, and low-level POSIX calls (`open`, `writev`, `fsync`, `fstat`, `read`, `unlink`, `rename`, `posix_fallocate`). It is used by `XrdOfsChkPnt` and startup recovery in `XrdOfsConfigCP`.

## Risks and Edge Cases

- `RestoreInfo()` reads the entire checkpoint file into memory; `MaxSZ` limits normal generation, but corrupted or externally injected files could be large.
- `Destroy()` returns `errno` as a positive value on unlink failure, while most other methods return `-errno`; callers mostly treat nonzero as failure but sign consistency is a risk.
- `ErrState()` appends `err`, producing names like `.ckperr`; recovery logic specifically recognizes that suffix.
- A comment says zero-length files are "not committed"; this relies on create/truncate failure paths preserving that convention.
- `Reserve()` increases allocated space but not `ckpSize` until `Append()`; restore accepts zero-filled preallocated tails.
- The checkpoint filename sequence is process-local, seeded by seconds; `O_EXCL` protects collisions but high concurrency after restart still depends on sequence uniqueness and retry behavior outside this class.

## Test Signals

Tests should create a checkpoint, validate xattr/header source lookup, append multiple overlapping segments, ensure restore vectors are reversed, simulate CRC corruption, truncated headers, truncated segments, zero-length files, and preallocated zero tails. Space-reservation failure and unlink/rename failure should be fault-injected. Recovery tests should verify `Target()` works with and without xattrs.
