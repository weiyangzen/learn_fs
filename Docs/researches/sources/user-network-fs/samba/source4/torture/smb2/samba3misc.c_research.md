<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c -->
# sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c

## Purpose
`samba3misc.c` provides SMB2 coverage for Samba3-specific miscellaneous behavior. Its current test, `localposixlock1`, verifies that an SMB2 byte-range lock conflicts correctly with a local POSIX lock taken directly on the underlying exported file, and that a blocking SMB2 lock completes once the local POSIX lock is released.

## Important APIs, Types, And Functions
The file defines `CHECK_STATUS`, `BASEDIR`, and a local `WAIT_FOR_ASYNC_RESPONSE` loop. `torture_smb2_tree_disconnect_timer()` is a tevent timer callback that disconnects the tree's underlying `smbXcli_conn` with `NT_STATUS_CTX_CLIENT_QUERY_TIMEOUT` if the blocking lock never completes. `torture_samba3_localposixlock1()` is the actual test, and `torture_smb2_samba3misc_init()` registers it as `smb2.samba3misc.localposixlock1`.

The test uses Samba SMB2 helpers (`torture_smb2_testdir()`, `torture_smb2_testfile()`, `smb2_lock()`, `smb2_lock_send()`, `smb2_lock_recv()`, `smb2_util_close()`, `smb2_deltree()`), POSIX calls (`open()`, `fcntl(F_SETLK)`, `close()`), `struct flock`, `struct smb2_lock`, `struct smb2_lock_element`, and the event loop/timer APIs.

## Control Flow
The test creates `samba3misc.smb2`, opens a test file over SMB2, and computes the corresponding local filesystem path from `--option=torture:localdir=<LOCALDIR>`. It opens that local path and takes a one-byte write lock at offset zero with `fcntl(F_SETLK)`.

It then sends an SMB2 exclusive byte-range lock with `SMB2_LOCK_FLAG_FAIL_IMMEDIATELY` and expects `NT_STATUS_LOCK_NOT_GRANTED`. Next it sends a blocking SMB2 exclusive lock asynchronously, arms a five-second disconnect timer, waits until the async request reaches a cancelable/pending state, closes the local file descriptor to release the POSIX lock, and expects `smb2_lock_recv()` to return `NT_STATUS_OK`.

## State And Persistence
State is split between server-side SMB2 open/lock state and a direct local POSIX byte-range lock on the same backing file. The test depends on the server honoring local POSIX lock conflicts for ordinary SMB2 clients when `posix locking = yes`. Persistent filesystem artifacts are removed with `smb2_deltree()` at the end, and the local descriptor is closed on all cleanup paths.

## Dependencies And Integration Points
The test requires a Samba share whose server-side path is also locally accessible to the torture process through `torture:localdir`. It depends on POSIX locking support in the underlying filesystem and Samba3 locking integration. It integrates with the SMB2 torture suite as `SMB2 Samba3 MISC`.

## Risks
The test will fail or be skipped by assertion if `torture:localdir` is not configured, if the local path does not match the SMB share path, if the filesystem does not implement advisory locks as expected, or if `posix locking = no`. The timer disconnect is a safety net, but timeout behavior may mask whether the failure was a missing lock conflict, an event-loop issue, or an unexpectedly long blocking lock.

## Test Signals
Expected signals are successful directory/file setup, successful local `open()` and `fcntl()` locking, immediate `NT_STATUS_LOCK_NOT_GRANTED` for the non-blocking SMB2 lock, pending behavior for the blocking SMB2 lock, and `NT_STATUS_OK` after closing the local descriptor. The final cleanup should close the SMB2 handle and remove `samba3misc.smb2`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/samba3misc.c -->
