# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postrm

Purpose: This Debian server-package post-removal script unregisters the init service on remove/purge and deliberately preserves database, log, and cluster files on purge.

Important operations: For `remove` or `purge`, it runs `update-rc.d -f foundationdb remove || :`. For `purge`, it prints instructions for manually deleting `/var/lib/foundationdb`, `/var/log/foundationdb`, and `/etc/foundationdb/fdb.cluster`.

Control flow: Action handling is simple conditional branching on `$1`. Destructive deletion commands and user deletion are commented out.

State and persistence behavior: Init registration is removed, but data/log/config state remains. This conservative behavior protects user data even on package purge.

Dependencies and integration points: It uses Debian `update-rc.d` and shell output. It complements `preinst`/`prerm` service stop behavior.

Risks: Users expecting purge to remove all package state may be surprised, but deleting database files automatically would be dangerous. Tests should verify no data/config removal occurs and that service registration is removed idempotently.
