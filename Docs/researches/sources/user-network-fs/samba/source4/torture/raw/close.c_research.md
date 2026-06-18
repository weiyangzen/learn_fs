# sources/user-network-fs/samba/source4/torture/raw/close.c

Purpose: This file performs focused SMB1 raw close, splclose, flush, and exit tests.

Important APIs, types, and functions: `torture_raw_close()` drives `smb_raw_close()`, `smb_raw_flush()`, `smb_raw_exit()`, `smb_raw_pathinfo()`, `create_complex_file()`, and cleanup helpers. Local macros `REOPEN` and `CHECK_STATUS` simplify repeated create/status checks.

Control flow: The test creates a file, closes it with an explicit future write time, verifies a second close returns invalid handle, then queries all-info to confirm only write time changed. It repeats close with write time zero and verifies the existing write time is preserved. It checks `RAW_CLOSE_SPLCLOSE` on a normal file, flush with a closed handle, flush-all, flush on an open handle, then calls `SMBexit` and verifies the handle is invalid.

State and persistence behavior: It creates `\\torture_close.txt`, mutates file timestamps, and unlinks the file during cleanup. `SMBexit` changes server-side PID/open-handle state for the session.

Dependencies and integration points: It depends on raw close/flush/pathinfo APIs, time conversion helpers, all-info dumping, and raw exit semantics. The function is registered through the broader raw suite via `torture/raw/proto.h`.

Risks: Timestamp precision and server time handling can cause false failures; `basetime` is rounded to an even second to reduce this. Cleanup calls `smbcli_close()` even when `fnum` may already be invalid, which is tolerated in this test style.

Test signals: Passing confirms close-time write timestamp handling, invalid-handle errors after close/exit, splclose error mapping, and flush/flush-all behavior.
