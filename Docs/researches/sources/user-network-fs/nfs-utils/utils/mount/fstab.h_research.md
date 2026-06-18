# sources/user-network-fs/nfs-utils/utils/mount/fstab.h

Purpose: exposes legacy mtab/fstab lookup and update interfaces.

Important APIs and types: defines `_PATH_FSTAB` fallback, `struct mntentchn` linked-list node, mtab state queries, backward mount/proc lookups, fstab file/spec lookups, and mtab lock/update routines.

Control flow and integration: legacy `mount.c` uses fstab checks for non-root mounts and mtab updates after mount. `nfsumount.c` uses mount/proc lookups and deletion/remount updates. The header is excluded from libmount builds.

State and persistence: declares access to implementation-owned in-memory mount lists and persistent `/etc/mtab` mutation routines.

Dependencies: includes `nfs_mntent.h` for mount-entry file wrappers and `struct mntent`.

Risks and tests: consumers must not free returned list nodes. Because `update_mtab()` can mutate system files, tests should use isolated mount table paths or mocks. Compile tests should cover non-libmount builds.
