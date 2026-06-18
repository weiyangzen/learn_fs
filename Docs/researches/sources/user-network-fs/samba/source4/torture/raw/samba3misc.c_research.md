# sources/user-network-fs/samba/source4/torture/raw/samba3misc.c

## Purpose
This file collects miscellaneous Samba3 regression and compatibility tests for raw SMB1 behavior. It covers FID/tree validation, NTSTATUS versus DOS error mappings, case-insensitive listing, interaction between local POSIX locks and SMB locks, root-directory FID opens, oplock/logoff behavior, and malformed OpenX name blobs.

## Important APIs, Types, And Functions
The first helper group builds OpenX requests from raw name blobs: `smb_raw_openX_name_blob_send()`, `smb_raw_openX_name_blob()`, and `raw_smbcli_openX_name_blob()`. Related wrappers `raw_smbcli_open()`, `raw_smbcli_t2open()`, and `raw_smbcli_ntcreate()` expose old open, trans2 open with EAs, and NTCreateX behavior for error-code tests.

Major exported tests are `torture_samba3_checkfsp`, `torture_samba3_badpath`, `torture_samba3_caseinsensitive`, `torture_samba3_posixtimedlock`, `torture_samba3_rootdirfid`, `torture_samba3_rootdirfid2`, `torture_samba3_oplock_logoff`, and `torture_samba3_check_openX_badname`. Async lock support uses `receive_lock_result()` and a `tevent` timer callback `close_locked_file()`.

## Control Flow
`torture_samba3_checkfsp()` creates a second tree connection and verifies invalid FID handling: a directory FID read on the owning tree returns `INVALID_DEVICE_REQUEST`, while using that FID on another tree returns `INVALID_HANDLE`; the same cross-tree invalid-handle check is applied to a normal file FID.

`torture_samba3_badpath()` opens one connection with NT status support and one with DOS error mapping, then compares `chkpath`, `getatr`, OpenX, T2Open, NTCreateX, SMBmv, and NT rename errors for malformed paths, files used as directories, exclusive-create collisions, and rename collisions. `torture_samba3_caseinsensitive()` confirms that listing `InSeNsItIvE\*` finds the expected entries created under `insensitive`.

`torture_samba3_posixtimedlock()` requires `torture:localdir`; it creates a file over SMB, opens the backing local path, places a POSIX write lock with `fcntl`, verifies an immediate SMB lock fails, then sends a timed SMB lock and closes the local fd via timer so the SMB lock can complete. The rootdir FID tests open files relative to an open root or directory FID. The oplock/logoff test queues a conflicting open, logs off the session, and verifies the transport remains usable via echo. The bad-name test sends a 65535-byte `0xcc` OpenX name blob and expects `OBJECT_NAME_INVALID`.

## State And Persistence Behavior
The tests create and delete small files/directories such as `testdir`, `insensitive`, `posixlock`, `dir1`, and `testfile`. `torture_samba3_badpath()` temporarily changes client configuration options (`nt status support`, `client ntlmv2 auth`) and restores them after opening the required connections. `torture_samba3_posixtimedlock()` touches both SMB server state and a local filesystem path to the same backing file.

## Dependencies And Integration Points
Dependencies include raw SMB open/rename/lock/echo/logoff APIs, `tevent`, local POSIX `open`, `fcntl`, and `close`, Samba loadparm mutation helpers, and configured test settings such as `share`, `samba3`, and `localdir`. The tests are individually registered by `raw.c` under `samba3checkfsp`, `samba3badpath`, `samba3caseinsensitive`, `samba3posixtimedlock`, `samba3rootdirfid`, `samba3rootdirfid2`, `samba3oplocklogoff`, and `samba3badnameblob`.

## Risks And Edge Cases
Several tests are highly environment-dependent. DOS versus NT error mapping requires the client options to take effect as intended. T2Open accepts Samba3-specific `EAS_NOT_SUPPORTED` behavior when configured. POSIX timed lock testing requires the local path to map to the same file the SMB server exports and requires `posix locking = yes`. `raw_smbcli_t2open()` and `raw_smbcli_ntcreate()` assign returned FIDs through the `openx` union member even for other open levels, which works only if the union layout matches expectations.

## Test Signals
Signals are mostly exact NTSTATUS or DOS-status comparisons. Additional signals include count of case-insensitive listing entries, async timed-lock completion with `NT_STATUS_OK`, successful relative opens through root directory FIDs, successful echo after ulogoff during an oplock break, and rejection of an oversized invalid OpenX name blob.
