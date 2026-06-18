<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c

Purpose: connects to a remote share and queries filesystem information using raw SMB fsinfo levels.

Important APIs and types: `enum fsinfo_stage`, `struct fsinfo_state`, `smb_composite_fsinfo_send`, `smb_composite_fsinfo_recv`, `fsinfo_connect`, `fsinfo_query`, and raw/composite callback adapters. It uses `smb_composite_connect_send`, `smb_raw_fsinfo_send`, and `smb_raw_fsinfo_recv`.

Control flow: `send` constructs a connect request from fsinfo input and inherited options from an existing `tree` argument, then enters `FSINFO_CONNECT`. On connection completion it allocates `union smb_fsinfo`, sets the requested level, sends the raw query on the newly connected tree, and advances to `FSINFO_QUERY`. Query completion stores the fsinfo union in `io->out`.

State and persistence: the returned `union smb_fsinfo` is allocated under state and stolen to the caller in recv. The file has no durable local storage; network-visible state is limited to opening an SMB session/tree and issuing the fsinfo transaction.

Risks: the `tree` parameter is used as a parent/options source while the operation opens a new tree, so callers need a live tree with valid transport/session options. Error handling maps raw query failures to composite error. Test signals include every supported fsinfo level, invalid credentials, missing event context, and ownership of `out.fsinfo` after recv.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/fsinfo.c -->
