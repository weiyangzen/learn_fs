# sources/user-network-fs/nfs-utils/systemd/rpc-pipefs-generator.c

Purpose: `rpc-pipefs-generator.c` creates runtime systemd units when the configured rpc_pipefs mount path differs from the default.

Important APIs and control flow: `main` reads `NFS_CONFFILE`, exits when `general/pipefs-directory` is absent or equals the default, rejects paths already mounted by a non-rpc_pipefs filesystem, and calls `generate_target`. `generate_target` escapes the path to a mount unit name, writes that mount unit with `What=sunrpc`, `Type=rpc_pipefs`, then writes `rpc_pipefs.target` requiring and ordering after it.

State, dependencies, and integration: Generated files are transient systemd generator output. It depends on nfs.conf, `/etc/mtab`, and `systemd_escape`.

Risks and test signals: `is_non_pipefs_mountpoint` uses string comparisons that can misread unusual mtab entries, and generated directories are minimally checked. Tests should cover default no-op, custom path, path escaping, already-mounted wrong type, and generator argument validation.
