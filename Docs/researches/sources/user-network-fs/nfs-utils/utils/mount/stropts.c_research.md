<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.c -->
# sources/user-network-fs/nfs-utils/utils/mount/stropts.c

## Purpose

`stropts.c` is the text-option mount path for `mount.nfs`. It validates user options, resolves server addresses, negotiates NFS version and transport choices, constructs final kernel mount option strings, and drives foreground/background retry behavior.

## Important APIs, types, and functions

The private `struct nfsmount_info` carries the requested spec, mountpoint, type, parsed options, extra mtab options, version, flags, fake mode, and background-child state. Public entry is `nfsmount_string`. Key helpers include `nfs_validate_options`, `nfs_set_version`, `nfs_append_addr_option`, `nfs_append_clientaddr_option`, `nfs_fix_mounthost_option`, `nfs_rewrite_pmap_mount_options`, `nfs_try_mount_v4`, `nfs_try_mount_v3v2`, `nfs_autonegotiate`, `nfsmount_fg`, `nfsmount_bg`, and `nfs_remount`.

## Control flow

`nfsmount_string` parses `extra_opts`, initializes `nfsmount_info`, and calls `nfsmount_start`. Validation parses `server:path` except on remount, chooses protocol family, strips user-supplied `addr`, determines version, and handles `sloppy`. Non-remount mounts choose foreground or background from rightmost `bg`/`fg`. The first attempt resolves addresses if needed, appends `addr=`, then either tries NFSv4 directly/autonegotiates or probes v2/v3 through rpcbind. V4 mounts add `clientaddr=` and format version/minor options. V3/V2 mounts rewrite protocol, port, mount protocol, mount version, and mount port from portmapper probes before calling `mount(2)`.

## State and persistence behavior

The module keeps mount attempt state in memory. It mutates the caller's `extra_opts` string to describe successful mounts for mtab, but deliberately records user-specified options before v3/v2 negotiation so unmount can renegotiate stale ports. It starts `rpc.statd` when locking is enabled and may fork background retry children through callers that honor `EX_BG`.

## Dependencies and integration points

It depends on NFS network helpers, rpcbind probing, config defaults, `parse_dev`, `parse_opt`, `mount(2)`, `getaddrinfo`, `nfs_error` reporting, and kernel-version checks from `version.h`. It integrates with `mount.nfs` command parsing through `stropts.h` and with `umount.nfs` via the mtab options it preserves.

## Risks and edge cases

Autonegotiation relies on errno classification from kernel mount attempts and rpcbind failures; misclassified failures can stop fallback too early or hide the true error. Static counters in `nfs_is_permanent_error` are process-global, so repeated attempts share history. User-provided `clientaddr` mismatch only warns, not fails. V4 rejects mountd-specific options by forcing fallback. Background retries can run for a long time by default. RDMA skips version/transport negotiation.

## Test signals

Tests should cover explicit v4 minor versions, default v4.2 fallback to v4.1/v4.0/v3, v3 rpcbind rewrites, remount bypass, `bg` retry classification, `retry=` parsing, `sloppy` handling on old/new kernels, lock/statd failures, clientaddr validation, mounthost/mountaddr combinations, RDMA no-negotiation behavior, and fake mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.c -->
