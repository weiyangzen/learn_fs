<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/mount.davfs.8.in -->
# Research: sources/user-network-fs/davfs2/man/mount.davfs.8.in

Purpose: source manual for `mount.davfs(8)`, the user-visible mount helper for exposing WebDAV resources as a local FUSE filesystem.

Important content/API surface: documents command forms via `mount -t davfs` and direct `mount.davfs`, mount options (`conf`, modes, uid/gid, `[no]user`, `username`, network and security flags), daemon privilege drop, WebDAV URL semantics, cache behavior, locks/lost-update handling, credentials and certificate file locations, environment variables (`DAVFS_PASSWORD`, proxy variables), and examples.

Control flow and integration: this file is configured by `man/meson.build` with `mandata`, replacing tokens such as `@PROGRAM_NAME@`, `@PACKAGE@`, `@SYS_CONF_DIR@`, `@SECRETSFILE@`, and `@SYS_CACHE_DIR@`. It is also an input to po4a, although Spanish translation is not configured for this page in `man/es/meson.build`.

State and persistence behavior described: explains in-memory directory metadata, on-disk file cache, delayed upload, permanent cache directories, PID files under `@SYS_RUN@`, lost+found backup files, secrets files, user config templates, and the fact that local ownership/permission changes are cached locally rather than represented on the server except execute bit metadata.

Dependencies/integration: must match implementation in `mount_davfs.c`, `cache.c`, `webdav.c`, `kernel_interface.c`, and defaults in `defaults.h`/Meson options. It documents FUSE kernel version 7 support and umount helper expectations.

Risks: incorrect docs here affect security-critical operator choices around user mounts, secrets readability, TLS certificate trust, and cache recovery. Some typos remain, but the behavioral content matches the cache and lock model observed in `cache.c`.

Test signals: generated manpage should render cleanly with configured values. Behavioral tests should compare documented options with parser support and verify examples for fstab escaping, credentials lookup, and unmount synchronization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/mount.davfs.8.in -->
