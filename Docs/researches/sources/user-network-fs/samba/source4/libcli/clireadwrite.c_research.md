# sources/user-network-fs/samba/source4/libcli/clireadwrite.c

## Purpose

`clireadwrite.c` provides synchronous SMB1 file read/write convenience wrappers. It reads with SMBreadX, writes with SMBwriteX, and offers an older SMBwrite path that does not bypass zero-byte writes.

## Important APIs, Types, and Functions

Public APIs are `smbcli_read()`, `smbcli_write()`, and `smbcli_smbwrite()`. They fill `union smb_read` or `union smb_write` and call `smb_raw_read()`/`smb_raw_write()`.

## Control Flow

`smbcli_read()` computes a read block size from negotiated `max_xmit`, caps it at 64 KiB, loops until requested bytes are read or the server returns a short read, and advances offset and output buffer. `smbcli_write()` similarly chunks writes using writeX and advances by bytes actually written until complete. `smbcli_smbwrite()` uses the legacy write command, including for zero-length requests, and loops until all bytes are written or the server writes zero.

## State and Persistence Behavior

Reads do not mutate remote file data. Writes mutate remote file content at supplied offsets. No local persistent state is held beyond loop counters and raw request unions.

## Dependencies and Integration Points

The file depends on raw SMB read/write helpers, negotiated transport `max_xmit`, `MIN_SMB_SIZE`, and valid tree/fnum state created by connection/open wrappers.

## Risks and Edge Cases

Errors return `-1`, losing NTSTATUS detail. Block-size calculations assume negotiated `max_xmit` is larger than protocol overhead; negative or tiny values can lead to problematic sizes. `smbcli_write()` advances both offset and buffer by bytes written. Offset types depend on `off_t` width.

## Test Signals

Tests should cover zero-length reads/writes, EOF short reads, large transfers spanning many chunks, small `max_xmit`, write modes for named pipes/cache behavior, and large offsets.
