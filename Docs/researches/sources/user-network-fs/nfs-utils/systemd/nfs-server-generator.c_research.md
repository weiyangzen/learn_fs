# sources/user-network-fs/nfs-utils/systemd/nfs-server-generator.c

Purpose: `nfs-server-generator.c` emits a drop-in for `nfs-server.service` that orders it with exported filesystems and loopback NFS mounts.

Important APIs and control flow: `main` validates the generator argument layout, disables syslog, reads `/etc/exports` and `/etc/exports.d`, creates `nfs-server.service.d/order-with-mounts.conf`, and writes `[Unit]` dependency lines. For exported paths it emits `RequiresMountsFor` unless the export has an explicit mountpoint or a covering fstab entry with `noauto`. For fstab `nfs`/`nfs4` mounts it emits `Before=<escaped>.mount`.

State, dependencies, and integration: It reads exports, `/etc/fstab`, and uses `systemd_escape`. Generated files live in the systemd generator output directory for one boot transaction.

Risks and test signals: `is_unique` stores export path pointers without freeing, fstab prefix matching can be broad, and paths with quotes are only partially handled. Tests should run generator fixtures for spaces, duplicate exports, `noauto`, loopback mounts, and empty exports.
