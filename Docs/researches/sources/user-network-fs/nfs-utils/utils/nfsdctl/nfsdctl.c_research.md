## sources/user-network-fs/nfs-utils/utils/nfsdctl/nfsdctl.c

Purpose: Implements `nfsdctl`, an administrative CLI and interactive shell for controlling kernel nfsd and lockd through generic netlink. It exposes `status`, `threads`, `version`, `listener`, `pool-mode`, `nlm`, and `autostart`.

Important APIs/types/functions: Local state uses `struct nfs_version`, `struct server_socket`, `nfsd_versions`, and `nfsd_sockets`. Netlink helpers include `netlink_sock_alloc`, `netlink_msg_alloc`, family setup, policy probing, shared callbacks, and parsers for status, version, listener, thread, pool, and lockd attributes. Command handlers are dispatched through `parse_command` and `func[]`.

Control flow: `main` reads `nfs.conf`, parses global options, opens netlink, queries policy support, then runs one command or a readline loop. Set commands fetch current kernel state, mutate local arrays, serialize nested netlink attributes, and wait for ACK/finish callbacks.

State and persistence: Persistent configuration comes from `/etc/nfs.conf`; runtime truth is kernel nfsd/lockd state. `autostart` applies configured versions, listeners, lockd ports, thread counts, scope, lease/grace times, dynamic min threads, and optional filehandle key hash.

Dependencies and integration: Uses libnl/genl, generated `nfsd_netlink.h` and `lockd_netlink.h`, readline, uuid, `nfslib`, `conffile`, `xlog`, module autoload via `modprobe`, and kernel support advertised by netlink policy.

Risks and test signals: Risk is high around kernel-version compatibility, listener parsing, global fixed arrays, netlink attr bounds, IPv6 availability, and privileged execution. Useful tests exercise unsupported attributes, invalid listener/version syntax, no-listener thread starts, `autostart` from representative configs, and mocked netlink replies.
