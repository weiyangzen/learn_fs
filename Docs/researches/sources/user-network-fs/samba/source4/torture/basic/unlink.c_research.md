# sources/user-network-fs/samba/source4/torture/basic/unlink.c

## Purpose
This file validates that unlinking an open file is denied even when the file was opened with delete-related access/share settings.

## Important APIs, types, and functions
The exported function is `torture_unlinktest()`. It uses `torture_setup_dir()`, `smbcli_open()`, `smbcli_unlink()`, `smbcli_close()`, `smb_raw_open()` with `RAW_OPEN_NTCREATEX`, `check_error()`, and `union smb_open`.

## Control flow
The test creates `\unlinktest\unlink.tst`, opens it with classic `smbcli_open()`, asserts unlink fails with sharing violation, closes and removes it, then recreates it using NT CreateX with full file rights and `NTCREATEX_SHARE_ACCESS_DELETE`. It again asserts unlink while open fails and verifies the error mapping.

## State and persistence
State is confined to `\unlinktest` and the single test file. The final NT CreateX handle is not explicitly closed before return, relying on harness/session cleanup; this is acceptable for the test intent but notable.

## Dependencies and integration points
The file complements rename/share-delete tests and uses both high-level and raw open paths. It depends on DOS/NT error mapping through `check_error()`.

## Risks
Servers that implement POSIX delete-on-open semantics differently may fail this compatibility expectation. The missing explicit close after the second open can leave transient state until connection cleanup.

## Test signals
Both unlink attempts must fail and report `ERRDOS/ERRbadshare` with `NT_STATUS_SHARING_VIOLATION`.
