<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c -->
# sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c

## Purpose

This file defines the `vfs.streams_xattr.streams-pwrite-hole` SMB2 torture test. It validates that the `vfs_streams_xattr` alternate data stream backend preserves sparse stream semantics: writing to the beginning and near the end of an ADS should expose zero-filled bytes in the unwritten hole when read back through SMB2.

## Important APIs, Types, and Functions

- `get_stream_handle()` creates the base test directory, base file, and named stream, returning an SMB2 handle for the stream.
- `read_stream()` wraps `smb2_read()` for an arbitrary stream offset and length.
- `test_streams_pwrite_hole()` is the single test body. It writes `WRITE_PAYLOAD` at offset `0` and at `ADS_OFF_TAIL`, reads `ADS_LEN` bytes, and checks payload placement plus zero fill.
- `torture_vfs_streams_xattr()` registers the suite and test under the VFS torture namespace.

## Control Flow

The test creates `smb2-testads`, opens `testdir/testfile:test_stream`, writes the canary string twice using `smb2_util_write()`, then reads the full 1024-byte ADS. It first asserts the read length is exactly `ADS_LEN`, then compares the two written regions and scans the gap byte by byte for `'\0'`. Cleanup frees the temporary talloc context, closes the stream handle if present, and removes the test tree with `smb2_deltree()`.

## State and Persistence Behavior

All state is remote SMB server state under `BASEDIR`. The test creates a directory, a file, and an ADS, then removes the tree at the end. No local files are persisted. Early `return false` paths after failed writes skip the common cleanup block, so a failed server write can leave the test tree behind.

## Dependencies and Integration Points

The file depends on the SMB2 torture helpers, SMB2 read/write calls, SMB2 testdir/testfile helpers, and the VFS torture registration in `vfs.c`. It is meaningful only against a share configured with streams support, typically `vfs_streams_xattr`.

## Risks and Edge Cases

The test relies on server behavior for sparse ADS reads and on `sizeof(WRITE_PAYLOAD)`, which includes the trailing NUL byte. Diagnostics on write failure print `sizeof(canary)`, where `canary` is a pointer, not the payload length; this affects reporting, not the write itself. Failed write paths bypass handle/tree cleanup.

## Test Signals

Pass signals are successful stream creation, exact 1024-byte readback, matching payload at offset `0` and offset `ADS_OFF_TAIL`, and all intervening bytes zero. Failure signals point to stream hole materialization, ADS length, xattr stream storage, or SMB2 read/write regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/streams_xattr.c -->
