# sources/user-network-fs/samba/source4/torture/smb2/read_write.c

## Purpose
This file provides SMB2 read/write torture tests for data integrity, invalid offset boundaries, max-file-size edge behavior, delete-on-close read/write behavior, and append/write-data access semantics.

## Important APIs, Types, And Functions
`torture_smb2_readwrite_init()` registers `rw1`, `rw2`, `invalid`, and `append`. The implementation uses `struct smb2_create`, `struct smb2_read`, `struct smb2_write`, `union smb_setfileinfo`, `union smb_fileinfo`, `smb2_create`, `smb2_write`, `smb2_read`, `smb2_setinfo_file`, `smb2_getinfo_file`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `smb2_deltree`, and torture buffer helpers such as `generate_random_buffer()`.

## Control Flow
`run_smb2_readwritetest()` removes `torture2.lck`, opens it read/write on one tree and read-only on another tree, then runs `torture_numops` iterations. Each iteration chooses a random buffer length up to 128 KiB, writes it at offset 0 through the first handle, reads the same length through the second handle, and compares bytes exactly. `run_smb2_wrap_readwritetest()` reuses the same tree for both sides to cover same-session behavior.

`test_rw_invalid()` creates `smb2_writetest.dat`, marks it delete-on-close, writes 64 KiB, then probes read offsets around EOF, `INT64_MAX`, `INT64_MIN`, and negative values encoded as unsigned. It also checks write behavior for negative offsets, zero-length writes at high offsets, a Samba max-file-size boundary (`0xfffffff0000`), and target-specific disk-full versus Samba success at `MAXFILESIZE - 1`. `test_append()` verifies that `SEC_FILE_APPEND_DATA` alone does not force SMB2 writes to append when an explicit offset is supplied, then verifies a write-data handle can extend the file at offset 1000.

## State And Persistence
The tests create temporary files `torture2.lck` and `smb2_writetest.dat`, set delete-on-close in one invalid-path test, and remove files during cleanup. Random test buffers are stack allocated. Handles are zeroed after successful close so cleanup can avoid double-closing.

## Dependencies And Integration Points
The file depends on SMB2 client calls, torture framework globals such as `torture_numops`, target detection macros (`TARGET_IS_SAMBA3`, `TARGET_IS_SAMBA4`), and utility helpers from `torture/util.h` and `torture/smb2/proto.h`. It integrates with both two-connection and same-connection torture registration.

## Risks
The random integrity loop can be expensive or flaky if `torture_numops` is very high or the backing share has caching/consistency bugs. The invalid-offset expectations are sensitive to signed/unsigned offset handling and server maximum file size policy. The delete-on-close setup means cleanup and subsequent operations depend on handle lifetime. Append semantics are subtle because SMB2 explicit offsets differ from POSIX append intuition.

## Test Signals
Signals include exact read/write statuses, `w.out.nwritten`, returned read lengths, byte-for-byte buffer equality, file size checks after append/write-data scenarios, and target-specific handling of the max-file-size boundary.
