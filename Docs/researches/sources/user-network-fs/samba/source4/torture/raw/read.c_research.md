# sources/user-network-fs/samba/source4/torture/raw/read.c

## Purpose
This file implements the raw SMB read test suite. It validates legacy `SMBread`, `SMBlockread`, `SMBreadX`, `SMBreadbraw`, and READX execute-permission behavior across empty files, EOF, invalid handles, large reads, locked ranges, large offsets, alignment, and access-mask combinations.

## Important APIs, Types, And Functions
The exported suite factory is `torture_raw_read()`, which registers `test_read`, `test_readx`, `test_lockread`, `test_readbraw`, and `test_read_for_execute`. Shared helpers `setup_buffer()` and `check_buffer()` create deterministic pseudo-random data based on a seed. The test code uses `union smb_read`, `union smb_open`, `union smb_write`, raw calls `smb_raw_read()`, `smb_raw_read_send()`, `smb_raw_open()`, `smb_raw_write()`, and classic helpers such as `smbcli_open`, `smbcli_write`, `smbcli_lock`, and `smbcli_lock64`.

## Control Flow
Each read variant creates `\testread\test.txt`, runs protocol-specific reads, validates status and byte counts, then tears down the directory. `test_read()` covers `RAW_READ_READ`, including empty/zero reads, invalid FID, short reads, maximum offsets, large count handling, and write-lock conflict. `test_lockread()` first checks negotiated `lockread_supported`, then validates the implicit locking behavior of LOCKREAD and expected `LOCK_NOT_GRANTED`/`FILE_LOCK_CONFLICT` outcomes.

`test_readx()` is the broadest path: it validates empty and zero reads, invalid handles, reserved response words, Unicode alignment via `CHECK_READX_ALIGN`, short reads, `mincnt`/`maxcnt` combinations, page-sized and 64 KiB reads, `CAP_LARGE_READX`, locked regions, and large-file offsets when `CAP_LARGE_FILES` is set. `test_readbraw()` checks raw-read behavior, including its unusual success-with-zero-data behavior for invalid handles and locked regions. `test_read_for_execute()` verifies `FLAGS2_READ_PERMIT_EXECUTE`: execute-only opens can read only when `read_for_execute` is true, while read-data opens work with or without the flag.

## State And Persistence Behavior
All tests use the transient `\testread` directory and remove it with `smbcli_deltree()`. They create and close SMB file handles, take byte-range locks, manipulate `cli->session->pid` to simulate a different locker, and in one path call `smb_raw_exit()` before cleanup. Data persistence is temporary but deliberately writes up to 90,000 bytes to exercise large transfer paths.

## Dependencies And Integration Points
The file depends on negotiated capability flags (`CAP_LARGE_FILES`, `CAP_LARGE_READX`), transport feature booleans (`lockread_supported`, `readbraw_supported`), raw SMB read/open/write APIs, torture settings such as `read_support`, and the shared raw torture registration in `raw.c`. It also depends on low-level SMB request access to inspect READX response words.

## Risks And Edge Cases
The deterministic buffer helper uses global `srandom()`/`random()`, so it is not thread-local. Large-read expectations intentionally allow Samba's large-read extension in some cases. Lock behavior is sensitive to server byte-range lock semantics and PID handling. READBRAW has legacy behavior where some errors are represented as OK with zero bytes, so refactoring must preserve protocol-specific expectations rather than normalizing all read paths.

## Test Signals
Pass signals include exact NTSTATUS values, exact read byte counts, byte-for-byte buffer validation, zeroed READX reserved fields, aligned READX data offsets when Unicode is negotiated, and correct access-denied behavior for execute-only reads without `read_for_execute`. Failures print assertion context, expected status/value, buffer offsets, or protocol-specific diagnostics.
