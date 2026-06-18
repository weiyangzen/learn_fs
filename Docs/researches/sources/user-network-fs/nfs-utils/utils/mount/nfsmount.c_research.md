# sources/user-network-fs/nfs-utils/utils/mount/nfsmount.c

Purpose: performs legacy binary-data NFSv2/v3 mounts using the MOUNT RPC protocol to retrieve file handles before calling `mount(2)`.

Important APIs: `nfsmount()` is the exported mount path. `parse_options()` handles rsize/wsize/timeouts/cache flags, mountd/NFS program/version/port/proto options, security flavor, SELinux context, and locking/cache flags. `nfs_call_mount()` probes both NFS and mountd, opens a mountd client, and calls `MOUNTPROC_MNT` or `MOUNTPROC3_MNT`. Inline `nfs2_mount()`/`nfs3_mount()` wrap RPC calls.

Control flow: `nfsmount()` parses `host:dir`, resolves host, initializes defaults and pmap requests, checks compatibility, loops through retry/background behavior, calls MOUNT, validates returned status and security flavor support, copies file handles into kernel mount data, starts statd if remote locking is required, appends `addr=`, then calls `mount(2)` unless fake.

State and persistence: static `struct nfs_mount_data` and buffers are reused per process; mtab options are returned via `extra_opts`. Remote state includes MOUNT rmtab registration, undone via UMNT on security flavor mismatch.

Dependencies and integration: libtirpc, network probing/statd helpers, error mapping, Linux version detection, global frontend flags.

Risks: legacy path is IPv4-oriented and mutates option strings; MOUNT retry loops can take minutes; security flavor negotiation must match server-provided flavor list. Test signals include mount v2/v3 success, RPC status mapping, bg retry/exponential wait for missing mountpoint, bad option/sloppy behavior, nolock/statd behavior, and mount syscall failures.
