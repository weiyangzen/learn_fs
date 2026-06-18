# sources/user-network-fs/nfs-utils/utils/mount/network.c

Purpose: common network, rpcbind, protocol/version parsing, callback address, statd, and advisory unmount helpers for NFS mount/umount.

Important APIs: address conversion `nfs_lookup()`, `nfs_gethostbyname()`, `nfs_string_to_sockaddr()`, `nfs_present_sockaddr()`, and `nfs_callback_address()`. Probing functions `probe_bothports()` and `nfs_probe_bothports()` fill NFS and mountd `pmap` tuples. Option parsers include `nfs_nfs_version()`, `nfs_nfs_protocol()`, `nfs_nfs_proto_family()`, `nfs_mount_proto_family()`, and `nfs_options2pmap()`. RPC helpers include `mnt_openclnt()`, `mnt_closeclnt()`, `clnt_ping()`, `nfs_advise_umount()`, `nfs_call_umount()`, `nfs_umount_do_umnt()`, and `start_statd()`.

Control flow: mount code resolves hosts, parses requested versions/transports/ports, probes rpcbind and NULL RPC calls in ordered protocol/version lists, then supplies discovered endpoints to mount RPCs. Unmount code reconstructs endpoint data from stored options, skips UMNT for NFSv4, resolves mountd, and sends advisory UMNT.

State and persistence: global default family/protocol can be influenced by config. External state includes DNS, local interfaces, rpcbind, remote NFS/mountd services, rpc.statd, and stored mount options.

Dependencies and integration: libtirpc, rpcbind/nfsrpc helpers, parse_opt, conffile, nfslib, network interfaces, and Linux IPv6 preferences.

Risks: network probing has many fallback/error paths; NFSv4-vs-v3 detection uses EAGAIN signaling; address-family defaults depend on build-time IPv6 support. Test signals include IPv4/IPv6 lookup, proto/version parse errors, fixed and discovered pmap combinations, timeout handling, statd start, local address matching, and NFSv4 UMNT skip.
