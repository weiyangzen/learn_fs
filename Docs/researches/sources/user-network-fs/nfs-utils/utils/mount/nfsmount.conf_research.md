# sources/user-network-fs/nfs-utils/utils/mount/nfsmount.conf

Purpose: sample/default NFS mount configuration file consumed by `configfile.c` when mount config support is enabled.

Important content: documents section forms `[MountPoint "..."]`, `[Server "..."]`, and `[NFSMount_Global_Options]`. It lists commented options for default and mandatory protocol version, network protocol, retries, cache attribute times, ACLs, background/foreground behavior, hard/soft, locking, READDIRPLUS, read/write sizes, sloppy parsing, sharecache, timeo, mountd host/port/protocol/version, server port, RPCGSS security flavors, interrupt behavior, lookupcache, and noatime.

Control flow and integration: no executable code; options here map through aliases and parsing in `configfile.c`, then through protocol/version parsers in `network.c` and option parsers in `nfsmount.c`/`nfs4mount.c` or string mount paths.

State and persistence: if installed as `/etc/nfsmount.conf`, uncommented settings persistently alter mount defaults system-wide.

Dependencies: syntax depends on nfs-utils conffile section/tag handling.

Risks and tests: examples must stay aligned with parser-supported names and case behavior. Test signals include installing a config with each documented option, verifying mount option output, and ensuring commented defaults do not alter behavior.
