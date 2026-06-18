<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/man/umount.davfs.8.in -->
# Research: sources/user-network-fs/davfs2/man/umount.davfs.8.in

Purpose: source manual for `umount.davfs(8)`, the helper called by `umount(8)` to wait for davfs2 cache synchronization before unmount completion.

Important content/API surface: documents `umount dir` and root-only direct helper invocation, `-h`/`-V`, ignored compatibility flags (`-f -l -n -r -v -t`), lookup of PID files under `@SYS_RUN@`, and fallback `umount -i` if the daemon reports serious errors.

Control flow and integration: configured by `man/meson.build` into `man8`. It references `mount.davfs(8)`, `umount(8)`, `davfs2.conf(5)`, and `fstab(5)`. The behavior described corresponds to the daemon/cache shutdown path in `cache.c` and the helper source `umount_davfs.c` included by `src/meson.build`.

State and persistence behavior described: emphasizes that local cached dirty files may take seconds to hours to write back to the WebDAV server; the helper blocks so `umount` returns only after synchronization, mirroring local filesystem expectations.

Dependencies: relies on PID-file conventions, daemon cooperation, and cache close logic. `_netdev` mount option is recommended so the OS treats the mount as network-backed.

Risks: lazy/forced unmount bypasses normal synchronization guarantees. If docs and helper behavior diverge, users may assume writes are durable when dirty cache data remains local.

Test signals: generated manpage rendering, helper CLI option compatibility, integration tests that dirty a cached file then invoke `umount` and confirm the helper waits for upload or returns an error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/man/umount.davfs.8.in -->
