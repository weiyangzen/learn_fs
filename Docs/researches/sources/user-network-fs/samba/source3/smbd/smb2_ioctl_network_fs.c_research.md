# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_network_fs.c

Purpose: handles network-filesystem FSCTLs for server-side copychunk, resume keys, network interface enumeration, and validate-negotiate-info.

Important APIs and types: `smb2_ioctl_network_fs()` dispatches controls. `fsctl_srv_copychunk_send()` / `fsctl_srv_copychunk_recv()` implement `FSCTL_SRV_COPYCHUNK` and `_WRITE`. `copychunk_check_limits()` and `copychunk_pack_limits()` validate and report server limits. `fsctl_network_iface_info()` emits multichannel interface data. `fsctl_validate_neg_info()` compares client-provided negotiation state to the live connection. `smb2_ioctl_network_fs_offload_read_done()` packages resume keys.

Control flow: copychunk validates output room, NDR-pulls request data, checks chunk count/length/total limits, stores the source token, and loops through chunks with `SMB_VFS_OFFLOAD_WRITE_SEND()`. Zero-chunk requests still call VFS once for macOS copyfile semantics. Network interface info requires empty input and multichannel enabled, reloads local interfaces, filters CTDB movable public IPs except the current address, skips non-IP or zero-speed interfaces, and NDR-pushes a linked response. Validate-negotiate parses capabilities, GUID, security mode, and dialects, recomputes dialect match, and sets disconnect on mismatch. Resume-key reads a VFS offload token and packages it into `req_resume_key_rsp`.

State and persistence: copychunk mutates destination file data/extents. Validate-negotiate may terminate the connection. Interface and resume-key paths are read-only from this file's perspective.

Dependencies and integration: depends on generated IOCTL NDR, VFS offload hooks, `smb2_negprot.c` connection state, multichannel client state, interface discovery, tsocket helpers, CTDB public IP iteration, and common IOCTL response handling.

Risks: copychunk error responses can include data and must stay aligned with front-door classification. Interface enumeration must not advertise movable cluster IPs incorrectly. Validate-negotiate mismatch intentionally disconnects the transport. Copychunk total-length assumptions should be revisited if limits change.

Test signals: cover copychunk limit errors with packed limits, partial chunk failure response, zero-chunk path, resume-key token size mismatch, multichannel disabled mapping, CTDB movable IP filtering, validate-negotiate success, and each mismatch causing disconnect.
