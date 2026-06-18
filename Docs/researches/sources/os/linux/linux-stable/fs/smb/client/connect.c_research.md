# File Research: sources/os/linux/linux-stable/fs/smb/client/connect.c

This file is the CIFS/SMB client connection orchestrator. It owns TCP session lifecycle, SMB session setup, tree connection setup, reconnect/failover, demultiplexing inbound SMB PDUs, superblock reuse matching, multiuser tcon links, mount/umount connection plumbing, socket creation, NetBIOS session setup, and protocol/session negotiation.

Main responsibilities:
- Maintains `TCP_Server_Info` state transitions across `CifsNew`, `CifsNeedNegotiate`, `CifsGood`, `CifsNeedReconnect`, and `CifsExiting`.
- Starts and stops the `cifsd` demultiplex thread via `cifs_get_tcp_session()` and `cifs_put_tcp_session()`.
- Reads SMB frames from sockets or SMB Direct, dispatches responses to matching MIDs, handles compound responses, oplock breaks, malformed PDUs, SMB transform headers, and credit updates.
- Implements reconnect paths through `cifs_reconnect()`, `cifs_reconnect_once()`, `cifs_signal_cifsd_for_reconnect()`, and `cifs_mark_tcp_ses_conns_for_reconnect()`.
- Under `CONFIG_CIFS_DFS_UPCALL`, reconnect can fail over across cached DFS targets using `reconnect_dfs_server()` and target hints.
- Matches and reuses TCP sessions, SMB sessions, tree connections, and superblocks only when transport, namespace, security, dialect, signing, user credentials, mount flags, prepath, and tree options are compatible.
- Creates IPC tcons for session-level operations and ordinary tcons for mounted shares.
- Handles SMB3 features during tcon setup: encryption, persistent/resilient handles, POSIX extensions, directory leasing, witness, fscache cookies, and multichannel interface polling.
- Builds mount context flows through `cifs_mount_get_session()`, `cifs_mount_get_tcon()`, and `cifs_mount()`.
- Manages multiuser `tcon_link` objects in a per-superblock red-black tree and prunes idle links.

Important flows:
- Initial mount: `cifs_setup_cifs_sb()` loads NLS and mount flags, `cifs_mount()` obtains server/session/tcon, checks DFS remoteness when appropriate, installs the master tlink, and schedules multichannel work if requested.
- TCP connect: `ip_connect()` tries port 445 first if no port is set, then port 139; `generic_ip_connect()` creates/binds/connects the socket and optionally runs `ip_rfc1001_connect()`.
- Receive path: `cifs_demultiplex_thread()` allocates buffers, reads RFC1002 headers, validates SMB response type, reads to MID, finds MID handlers, handles transformed responses, dispatches callbacks, and reconnects after repeated I/O timeouts.
- Reconnect: socket teardown marks submitted MIDs retryable, resets credits/session keys, marks affected sessions and tcons for reconnect, reconnects transport, then wakes waiters and schedules negotiation.
- Session setup: `cifs_get_smb_ses()` reuses compatible sessions or allocates a new one, negotiates protocol, performs session setup, supports alternate password retry, stores channel signing keys, and creates IPC.
- Tree setup: `cifs_get_tcon()` reuses compatible tcons or performs tree connect and applies share/mount options.

Concurrency and lifetime:
- Uses `cifs_tcp_ses_lock`, per-server `srv_lock`, per-session `ses_lock`/`chan_lock`, per-tcon `tc_lock`, MID queue locks, and workqueue cancellation to serialize state changes.
- Reference counts exist at each layer: server `srv_count`, session `ses_count`, tcon `tc_count`, and tlink `tl_count`.
- Demux cleanup wakes blocked requests and callbacks before freeing server memory.
- Multiuser tlink construction uses `TCON_LINK_PENDING` and `wait_on_bit()` to avoid duplicate per-UID tcon construction.

External dependencies:
- Calls dialect-specific operations through `server->ops`.
- Uses DFS helpers from `dfs.c`/`dfs_cache.c` when DFS upcall support is enabled.
- Uses DNS resolver helpers for reconnect hostname refresh.
- Uses SMB Direct helpers when RDMA is enabled.
- Integrates witness notifications, fscache, multichannel, keyring credentials, and optional legacy CIFS Unix extensions.

Research notes:
- This file is the central connection state machine for the SMB client.
- Reuse matching is deliberately conservative; small option differences prevent unsafe sharing.
- DFS support changes both mount and reconnect semantics because a logical path may reconnect to a different server/share.
- Error handling frequently converts transport loss into reconnect signals and MID callbacks rather than returning raw socket state to callers.
