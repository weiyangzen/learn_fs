# sources/user-network-fs/nfs-utils/utils/mount/nfs4mount.c

Purpose: performs legacy binary-data NFSv4 mounts.

Important APIs: `nfs4mount(spec, node, flags, extra_opts, fake, running_bg)` parses `host:dir`, resolves IPv4 server/client addresses, parses NFSv4-specific options, pings server NFS program v4, fills `struct nfs4_mount_data`, and calls `mount(2)`. Helpers include `parse_sec()`, `parse_devname()`, `fill_ipv4_sockaddr()`, and `get_my_ipv4addr()`.

Control flow: mount options populate rsize/wsize/timeouts/cache flags/proto/port/clientaddr/security flavors. If `bg` is requested and the foreground attempt should background, the function returns `EX_BG`. Otherwise it retries until timeout, accepting only supported RPC responses. Successful probe can update clientaddr based on the chosen local route.

State and persistence: uses static buffers and mount data for one process. It appends `addr=<server-ip>` to options for mtab/umount use unless already running in background.

Dependencies and integration: uses `network.c` `clnt_ping`, pseudoflavor map, error helpers, kernel NFSv4 mount ABI, and global `progname`, `verbose`, `sloppy`.

Risks: IPv4-only parsing in this legacy path; `strtok` mutates option strings; support daemon lock checks are disabled. Test signals include sec flavor parsing, unsupported options with/without sloppy, retry/background behavior, clientaddr override, fake mount, and mount syscall failure reporting.
