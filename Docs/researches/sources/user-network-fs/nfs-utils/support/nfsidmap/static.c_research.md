# sources/user-network-fs/nfs-utils/support/nfsidmap/static.c

Purpose: `static.c` implements a static idmap plugin where principals or NFSv4 names are explicitly mapped to local passwd/group names in the `[Static]` section of idmapd configuration.

Important APIs and control flow: `static_getpwnam` and `static_getgrnam` look up `Static/<principal>` and resolve the configured local user or group through NSS. Principal/name callbacks return UID/GID from those helpers. `static_init` reads all static tags, resolves each as both user and group, and caches reverse UID/GID-to-principal lookups in 256-bucket LIST hash tables.

State, dependencies, and integration: Persistent plugin state is the in-memory `uid_mappings` and `gid_mappings` tables. Config and NSS remain the source of truth. The plugin exposes `static_trans` to libnfsidmap.

Risks and test signals: Reverse callbacks use `strcpy` and ignore the output `len`. Mapping nodes are never freed during plugin lifetime, and hash collisions are linear. Tests should cover duplicate UID/GID mappings, missing local accounts, reverse mapping buffer limits, and both `krb5`/`spkm3` principal paths.
