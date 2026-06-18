# File Research: sources/os/linux/linux-stable/fs/smb/client/cifssmb.c

## Role

SMB1/CIFS PDU construction, send, reconnect, and response parsing layer for the Linux SMB client. This file implements most legacy CIFS/SMB1 wire operations exposed through the client operation tables: negotiate, tree connect, file open/read/write/lock/close, path operations, Trans2 metadata queries, NT transact security descriptor and IOCTL paths, DFS referrals, POSIX/Unix extension calls, and xattr/EA support.

## Main Operation Families

- Connection and request setup:
  - `cifs_reconnect_tcon()` gates sends through server/session/tree reconnect handling and returns `-EAGAIN` for stale handle-based operations that the caller must retry after reopening.
  - `small_smb_init()`, `__smb_init()`, `smb_init()`, and `smb_init_no_reconnect()` allocate request buffers, assemble SMB headers, and update per-tree send stats.
  - `validate_t2()` and `validate_ntransact()` perform common Trans2/NTTransact response bounds checks before parsing parameter/data areas.
- Negotiation and session/tree lifetime:
  - `CIFSSMBNegotiate()` sends SMB1 dialect negotiation, parses server capabilities, signing/security mode, max buffer/read/write sizes, and extended security blobs.
  - `CIFSTCon()`, `CIFSSMBTDis()`, `CIFSSMBLogoff()`, and `CIFSSMBEcho()` implement tree connect/disconnect, session logoff, and echo keepalive.
- Namespace mutation:
  - `CIFSSMBDelFile()`, `CIFSSMBRmDir()`, `CIFSSMBMkDir()`, `CIFSSMBRename()`, `CIFSUnixCreateSymLink()`, `CIFSUnixCreateHardLink()`, `CIFSCreateHardLink()`, and `CIFSPOSIXDelFile()` build pathname-oriented SMB1/Trans2 requests with ASCII or UTF-16 pathname conversion.
  - `CIFSSMBRenameOpenFile()` renames by file handle using `TRANS2_SET_FILE_INFORMATION`.
- Opens and I/O:
  - `CIFSPOSIXCreate()`, `SMBLegacyOpen()`, and `CIFS_open()` implement POSIX open, legacy `OPEN_ANDX`, and NT create.
  - `CIFSSMBRead()`, `cifs_async_readv()`, `CIFSSMBWrite()`, `cifs_async_writev()`, and `CIFSSMBWrite2()` implement sync and async SMB1 reads/writes, including large-file offsets, `CountHigh` correction, netfs completion, signature verification, and credit return.
- Locks and handle operations:
  - `cifs_lockv()`, `CIFSSMBLock()`, and `CIFSSMBPosixLock()` send Windows and POSIX byte-range lock requests.
  - `CIFSSMBClose()` and `CIFSSMBFlush()` close and flush server handles.
- Reparse and compression FSCTLs:
  - `cifs_query_reparse_point()` opens a path with `OPEN_REPARSE_POINT`, sends `FSCTL_GET_REPARSE_POINT`, validates response layout, and returns the reparse buffer.
  - `cifs_create_reparse_inode()` creates a placeholder object, optionally writes EAs, sends `FSCTL_SET_REPARSE_POINT`, then fetches inode info or deletes the placeholder on failure.
  - `CIFSSMB_set_compression()` sends `FSCTL_SET_COMPRESSION` for a file handle.
- Metadata query/set:
  - `SMBQueryInformation()`, `CIFSSMBQFileInfo()`, `CIFSSMBQPathInfo()`, `CIFSSMBUnixQFileInfo()`, `CIFSSMBUnixQPathInfo()`, and `CIFSGetSrvInodeNumber()` query legacy, NT, and Unix metadata.
  - `CIFSSMBSetEOF()`, `CIFSSMBSetFileSize()`, `SMBSetInformation()`, `CIFSSMBSetFileInfo()`, `CIFSSMBSetFileDisposition()`, `CIFSSMBSetPathInfo()`, `CIFSSMBUnixSetFileInfo()`, and `CIFSSMBUnixSetPathInfo()` update EOF/allocation, basic attributes, delete disposition, and Unix uid/gid/mode/time fields.
- ACLs, security descriptors, and EAs:
  - POSIX ACL support converts between CIFS ACL wire entries and Linux `struct posix_acl`.
  - `CIFSSMBGetCIFSACL()` and `CIFSSMBSetCIFSACL()` use NT transact security descriptor calls.
  - `CIFSSMBQAllEAs()` and `CIFSSMBSetEA()` implement query/list/set extended attributes through Trans2 EA info levels.
- Directory and filesystem queries:
  - `CIFSFindFirst()`, `CIFSFindNext()`, and `CIFSFindClose()` manage SMB1 directory search handles and network search buffers.
  - `CIFSGetDFSRefer()` sends `TRANS2_GET_DFS_REFERRAL` through IPC tree state.
  - `SMBOldQFSInfo()`, `CIFSSMBQFSInfo()`, `CIFSSMBQFSAttributeInfo()`, `CIFSSMBQFSDeviceInfo()`, `CIFSSMBQFSUnixInfo()`, `CIFSSMBSetFSUnixInfo()`, and `CIFSSMBQFSPosixInfo()` populate `kstatfs` and tree filesystem capability fields.

## Control Flow and Integration

Most public functions follow a repeatable pattern: initialize an SMB header, encode parameters and path/data payloads, call `SendReceive()`, `SendReceive2()`, `SendReceiveNoRsp()`, or `cifs_call_async()`, validate the response when one is expected, copy/convert wire data into CIFS or VFS structures, release the CIFS buffer, and retry on `-EAGAIN` only when the operation is path-based and safe to rebuild.

The file integrates with shared CIFS state in `struct cifs_ses`, `struct cifs_tcon`, `struct TCP_Server_Info`, `struct cifs_sb_info`, and `struct cifsFileInfo`. It relies on helpers from sibling files for header assembly, path conversion, DFS referral parsing, inode refresh, signature checking, credit accounting, xattr/reparse helpers, and netfs subrequest termination.

## State, Locking, and Lifetime

- Reconnect paths coordinate with `session_mutex`, `ses_lock`, `chan_lock`, `srv_lock`, `need_reconnect`, session status, and server TCP status.
- Async I/O callbacks own mid completion, netfs progress flags, request result propagation, mid release, and credit return.
- Search state owns a network response buffer across `FindFirst`/`FindNext`; `FindNext` frees the previous search buffer only after a replacement response is accepted.
- Response buffers from `SendReceive2()` are released through `free_rsp_buf()`, while normal CIFS request buffers use `cifs_buf_release()` or `cifs_small_buf_release()`.

## Validation and Risk Notes

The file contains many explicit bounds checks for Trans2 data offsets, byte counts, reparse buffers, EA list lengths, ACL sizes, read sizes, and filesystem info sizes. Remaining risk is typical for old SMB1 code: many routines manually compute byte counts, offsets, padding, and UTF-16 name lengths, so correctness depends on matching exact wire layouts. Several comments mark historical compatibility behavior and older-server workarounds, especially around information levels, Unix extensions, EA sizing, and handle-based retry behavior.
