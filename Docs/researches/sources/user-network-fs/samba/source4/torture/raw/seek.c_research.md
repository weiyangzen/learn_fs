# sources/user-network-fs/samba/source4/torture/raw/seek.c

## Purpose
This file implements `torture_raw_seek()`, a focused raw SMB seek test. It validates `smb_raw_seek()` behavior for invalid handles, absolute/current/end-relative seeks, 32-bit maximum offsets, overflow behavior, and the relationship between legacy seek offsets and `RAW_FILEINFO_POSITION_INFORMATION`.

## Important APIs, Types, And Functions
`test_seek()` performs all checks using `union smb_seek`, `union smb_fileinfo`, and `union smb_setfileinfo`. It calls `smb_raw_seek()`, `smb_raw_fileinfo()`, `smb_raw_setfileinfo()`, `smb_raw_setpathinfo()`, `smbcli_open()`, `smbcli_write()`, `smbcli_read()`, and cleanup helpers. The public `torture_raw_seek()` simply invokes `test_seek()`.

## Control Flow
The test creates `\testseek\test.txt`, verifies an invalid FID returns `INVALID_HANDLE`, seeks to offset 17 from start, then seeks back three bytes relative to current. It seeks from end and compares the returned offset to `ALL_INFO.size`, seeks to `-1` from start and expects `0xffffffff`, then checks that file-position information remains zero after pure seek calls.

After writing two bytes, it verifies current seek position and file-position information after read/write operations. It opens a second handle, sets `RAW_SFILEINFO_POSITION_INFORMATION` to 25 on that handle, and confirms the first handle remains at position 1. Finally, it attempts path-based position setting and verifies handle positions are unaffected and pathinfo position is zero.

## State And Persistence Behavior
The test creates a transient `\testseek` directory and deletes it at the end. It uses two handles to the same file to prove position state is per handle. It writes and reads small byte buffers and calls `smb_raw_exit()` before deleting the tree.

## Dependencies And Integration Points
Dependencies are the raw seek, fileinfo, and setfileinfo APIs plus standard smbcli open/read/write helpers. `raw.c` registers this as the `seek` one-SMB test.

## Risks And Edge Cases
The test targets legacy 32-bit seek behavior, so sign extension and overflow expectations are subtle. It assumes seek calls do not update `POSITION_INFORMATION`, while actual reads and explicit setfileinfo do. Path-based position information is expected to be a no-op-like query returning zero, which may surprise implementers trying to unify handle and path state.

## Test Signals
Success is a sequence of exact status and offset checks: invalid handle, offsets 17/14/end/0xffffffff/999, position values 0/1/25, and isolation between two handles. Failures print the source line, actual status/value, and expected value.
