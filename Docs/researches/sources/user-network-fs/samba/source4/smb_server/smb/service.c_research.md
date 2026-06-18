# sources/user-network-fs/samba/source4/smb_server/smb/service.c

## Purpose
Builds SMB1 tree connections. It resolves a requested share, checks access and device type, creates `smbsrv_tcon`, initializes the selected NTVFS backend, and installs frontend callbacks for oplock breaks and handle management.

## Important APIs, Types, And Functions
- `smbsrv_tcon_backend()` is called by `reply.c` for `SMBtcon` and `SMBtconX`.
- `make_connection()` normalizes `\\SERVER\SHARE` paths, resolves `share_config`, checks hosts allow/deny, determines `NTVFS_DISK`, `NTVFS_IPC`, or `NTVFS_PRINT`, and validates client device strings.
- `make_connection_scfg()` allocates the tcon, derives NTVFS client capability flags, calls `ntvfs_init_connection()`, and registers oplock, address, and handle callbacks.

## Control Flow
For old `SMBtcon`, the caller passes service/password/device strings and receives `max_xmit` plus TID. For `SMBtconX`, the caller passes path/password/device blob fields and receives TID plus share options such as search bits, CSC policy, and DFS-root indication. On backend initialization failure, the partially created tcon is freed and `req->tcon` is cleared.

## State And Persistence
A successful tree connect creates a persistent `smbsrv_tcon` under the connection. The tcon owns its NTVFS context and later owns valid frontend file handles. Per-share type, share config, local/remote addresses, server ID, event context, message context, protocol level, and client capability bits are transferred into NTVFS initialization.

## Dependencies And Integration Points
Depends on Samba share configuration, socket access checks, loadparm, NTVFS initialization, and callback functions from `receive.c` and `request.c`. It is the bridge that lets later file operations in `reply.c`, `search.c`, `trans2.c`, and `nttrans.c` call the correct backend.

## Risks
The TODO for share-level password checking means share security semantics depend on higher layers or are incomplete in this path. Device type matching is compatibility-sensitive (`?????` wildcard vs `A:`, `IPC`, `LPT:`). Failure handling must not leave a half-valid tcon in `req->tcon`. DFS option bits are only advertised when both share and global DFS settings allow it.

## Test Signals
Cover disk/IPC/printer share type mapping, `\\server\share` normalization, missing share returning `BAD_NETWORK_NAME`, hosts allow/deny rejection, wrong device type rejection, level-II oplock capability propagation, NTVFS initialization failure cleanup, callback registration, and DFS/CSC option bits in `tconX` replies.
