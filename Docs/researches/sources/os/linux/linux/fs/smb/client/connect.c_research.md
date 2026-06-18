# File Research: sources/os/linux/linux/fs/smb/client/connect.c

## Purpose
Implements the CIFS/SMB client connection, session, tree-connect, mount, reconnect, socket receive, and per-superblock tcon-link lifecycle machinery. This is the central transport/session orchestration file for SMB mounts.

## Main Interfaces
- TCP/session lifecycle: `cifs_get_tcp_session()`, `cifs_put_tcp_session()`, `cifs_find_tcp_session()`.
- SMB session lifecycle: `cifs_get_smb_ses()`, `__cifs_put_smb_ses()`, `cifs_setup_session()`, `cifs_setup_ipc()`.
- Tree connection lifecycle: `cifs_mount_get_tcon()`, `cifs_put_tcon()`, `cifs_tree_connect()` in non-DFS builds.
- Mount/unmount: `cifs_setup_cifs_sb()`, `cifs_mount()`, `cifs_umount()`, `cifs_mount_put_conns()`.
- Reconnect: `cifs_reconnect()`, `cifs_signal_cifsd_for_reconnect()`, `cifs_mark_tcp_ses_conns_for_reconnect()`.
- Receive path: `cifs_read_from_socket()`, `cifs_read_iter_from_socket()`, `cifs_discard_from_socket()`, `cifs_handle_standard()`, `dequeue_mid()`.
- Multiuser tcon resolution: `cifs_sb_tlink()`, `cifs_sb_master_tcon()`.

## Control Flow
Initial mount setup builds a `cifs_sb_info`, resolves or creates a TCP transport, negotiates protocol, creates or reuses an SMB session, and then creates or reuses a tree connection. `cifs_mount()` has separate DFS and non-DFS implementations under `CONFIG_CIFS_DFS_UPCALL`; DFS builds delegate referral traversal to `dfs_mount_share()`, while non-DFS builds directly connect session and tcon, then reject remote DFS paths if DFS upcalls are unavailable.

The demultiplex thread `cifs_demultiplex_thread()` owns socket/RDMA receive processing. It reads RFC1002 headers, validates SMB response framing, finds matching MID entries, handles transformed/encrypted responses through dialect operations, invokes callbacks, returns credits, detects server timeout statuses, and schedules reconnects when needed.

Reconnect flow marks TCP sessions, SMB sessions, channels, and tcons as needing reconnect, aborts the socket/RDMA transport, retries IP or DFS target reconnect, resets credits, transitions through `CifsNeedNegotiate`, and wakes waiters. DFS reconnect uses cached referral target lists and updates target hints after a successful target selection.

## State And Synchronization
The file coordinates several shared state machines:
- `TCP_Server_Info::tcpStatus` under `srv_lock`.
- session status and multichannel reconnect bitmaps under `ses_lock` and `chan_lock`.
- pending MIDs under `mid_queue_lock`.
- request credits under `req_lock`.
- global TCP/session/tcon lists under `cifs_tcp_ses_lock`.
- per-superblock tcon links in an rbtree under `tlink_tree_lock`.

Lifetime is reference-counted through `srv_count`, `ses_count`, `tc_count`, and `tcon_link::tl_count`. Teardown carefully cancels delayed work, wakes wait queues, drains pending MIDs, releases sockets/RDMA state, and defers superblock cleanup with RCU.

## Integration Points
- Depends on dialect-specific `server->ops` callbacks for negotiate, session setup, tree connect/disconnect, echo, open protocol checks, DFS referrals, interface query, transforms, message validation, and credit handling.
- Calls DNS helpers from `dns_resolve.h` for reconnect hostname refresh.
- Calls DFS cache and traversal helpers when `CONFIG_CIFS_DFS_UPCALL` is enabled.
- Integrates SMB Direct through `smbdirect.h`.
- Integrates witness notifications through `cifs_swn.h`.
- Integrates fscache setup through `cifs_fscache_get_super_cookie()`.

## Notable Behaviors
- Existing TCP sessions are reusable only when protocol, hostname/address/port, source address, namespace, signing/security, RDMA, echo interval, offload, retransmission, and sharing options match.
- Existing SMB sessions are reusable only when security type, credentials, domain/user identity, charset, DFS root session, and channel limits match.
- Existing tcons are reusable only when tree name or DFS origin path, encryption, snapshot time, handle timeout, lease behavior, delete semantics, and POSIX extension state match.
- RFC1002 negative session responses during negotiate can trigger a one-shot reconnect with NetBIOS session establishment.
- Multiuser mounts lazily construct per-fsuid tcons and prune idle links from the superblock rbtree.
- Multichannel setup is queued asynchronously after successful mount to avoid blocking the core mount path.

## Risks And Review Focus
- Lock ordering and refcounting are subtle across TCP/session/tcon teardown, reconnect work, demux callbacks, and multichannel references.
- Reconnect status transitions must keep MIDs, waiters, credits, channels, sessions, and tcons consistent.
- DFS failover can change target server/share and therefore disables server inode assumptions and forces prefix-path behavior.
- Socket receive error handling must avoid leaving pending MIDs without callbacks.
- Credential handling uses sensitive frees; any new password/session-key field must follow the same pattern.
- Mount reuse matching is security-sensitive because incorrect reuse can cross credentials, signing, encryption, or DFS boundaries.
