# sources/user-network-fs/samba/source4/torture/smb2/read.c

## Purpose
This file implements SMB2 read torture tests, including EOF/min-count semantics, read-position behavior, directory-handle read errors, access-mask requirements, a regression for read response body padding, and delayed AIO cancel behavior.

## Important APIs, Types, And Functions
The main suite is registered by `torture_smb2_read_init()` with tests `eof`, `position`, `dir`, `access`, and `bug14607`. A separate `torture_smb2_aio_delay_init()` suite registers `aio_cancel` for shares using the `delay_inject` VFS module. Tests use `struct smb2_read`, `struct smb2_handle`, `union smb_fileinfo`, `DATA_BLOB`, `smb2_read`, `smb2_read_send/recv`, `smb2_cancel`, `smb2_util_write`, `smb2_util_close`, `torture_smb2_testfile`, `torture_smb2_testdir`, `torture_smb2_testfile_access`, low-level `smb2cli_read`, and `smb2cli_ioctl`.

## Control Flow
`test_read_eof()` creates a file, verifies empty-file read returns EOF, writes 64 KiB, and then probes reads at start, exactly EOF, zero-length EOF, one byte before EOF, and inconsistent `min_count` combinations. `test_read_position()` checks whether a read advances current position, with a Windows-specific expected value difference. `test_read_dir()` opens a directory and verifies reads normally return `INVALID_DEVICE_REQUEST`, with Windows-specific zero-length exceptions. `test_read_access()` proves read succeeds with read-data or execute rights but fails with only read-attributes. `test_read_bug14607()` validates normal `smb2_read` and raw `smb2cli_read` before and after enabling the Samba torture FSCTL that pads read response bodies to an 8-byte boundary. `test_aio_cancel()` sends an async read, waits until the request can be cancelled, sends cancel, and still expects the read receive path to complete OK.

## State And Persistence
Tests create `smb2_readtest.dat` and `smb2_readtest.dir`, write temporary 64 KiB buffers, and clean handles and files on completion. Temporary allocations use talloc contexts scoped to the tree or test. The bug14607 test modifies server-side torture behavior through `FSCTL_SMBTORTURE_GLOBAL_READ_RESPONSE_BODY_PADDING8`, which may persist for the server process beyond the immediate request depending on the test FSCTL implementation.

## Dependencies And Integration Points
The file depends on Samba SMB2 calls, tevent for async/cancel, torture helpers, `smbXcli_base`, and generated ioctl definitions for the SMB torture FSCTL. It integrates with target-specific settings through `torture_setting_bool(torture, "windows", false)` and expects the delay AIO suite to run only where delayed async reads are configured.

## Risks
The tests encode Windows/Samba behavioral differences for current file position and directory zero-length reads, so changing expectations needs target awareness. `bug14607` depends on a Samba-specific FSCTL and skips when unsupported. `test_aio_cancel()` relies on `req->cancel.can_cancel` eventually becoming true; without a delay-inject share it may complete too quickly or not exercise the intended path.

## Test Signals
Key signals are exact NTSTATUS results (`OK`, `END_OF_FILE`, `INVALID_DEVICE_REQUEST`, `ACCESS_DENIED`), returned read lengths, byte-for-byte buffer equality for `smb2_read` and `smb2cli_read`, successful skip on unsupported FSCTL, and successful cancel/receive for delayed AIO reads.
