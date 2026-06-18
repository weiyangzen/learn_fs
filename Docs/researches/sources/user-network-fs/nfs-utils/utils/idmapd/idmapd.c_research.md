# sources/user-network-fs/nfs-utils/utils/idmapd/idmapd.c

Purpose: `idmapd.c` implements the NFSv4 ID mapping daemon for client rpc_pipefs upcalls and server nfsd procfs cache upcalls, converting between numeric ids and NFSv4 owner/group names.

Important APIs and types: `struct idmap_client` tracks each client channel fd, directory fd, path, libevent handle, and TAILQ membership. `main()` parses config/CLI, initializes nfsidmap, opens nfsd channels, watches rpc_pipefs with inotify, and runs libevent. `nfscb()` handles binary `struct idmap_msg` client messages. `nfsdcb()` handles text server cache upcalls. `idtonameres()` and `nametoidres()` call libnfsidmap conversion APIs. `addfield()`/`getfield()` escape/unescape procfs fields.

Control flow: startup loads `/etc/nfs.conf` and idmapd config, sets nobody user/group, daemonizes, initializes name mapping, then optionally opens server channels and/or scans client pipefs. Inotify/SIGUSR events rescan `clnt*` directories and add or remove client idmap channel events. Server callbacks parse auth/type/name-or-id, convert, and write cache records with expiry.

State and persistence: process globals store verbosity, cache expiry, pipefs path, nobody ids, event base, and inotify fd. Persistent external state lives in kernel nfsd cache channels, client rpc_pipefs idmap pipes, `/proc/sys/fs/nfs/idmap_cache_timeout`, and libnfsidmap configuration.

Dependencies and integration: libevent, inotify, nfsidmap, nfs-utils config/logging, passwd/group databases, `/proc/net/rpc/nfs4.*` caches, and rpc_pipefs.

Risks: malformed server upcalls can be dropped; `imconv()` has a fragile null-termination check; long or escaped fields depend on fixed `IDMAP_MAXMSGSZ`. Test signals include client-only/server-only modes, cache flush and timeout writes, inotify rescan, disappeared clients, user/group conversion success/failure, nobody fallback, and unprivileged config errors.
