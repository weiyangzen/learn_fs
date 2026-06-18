# File Research: sources/os/linux/linux/fs/coda/Kconfig

Kconfig entry for the Coda filesystem client.

Defines:
- `CONFIG_CODA_FS`: tristate “Coda file system support (advanced network fs)”.
- Dependency: `INET`.

Help text:
- Describes Coda as a network filesystem similar to NFS.
- Highlights disconnected operation, read/write server replication, authentication/encryption security model, persistent client caches, and write-back caching.
- Clarifies the kernel option enables Linux to act as a Coda client.
- Points to `Documentation/filesystems/coda.rst` and the Coda homepage.
- Module name is `coda`.
