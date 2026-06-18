# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_jail.c

## Role

Implements DragonFlyBSD jail creation, jail attachment, prison lifecycle/refcounting, jail IP address handling, jail sysctl reporting/control, and jailed privilege checks. It is important to filesystem research because jail roots are namecache handles, attach uses chroot, and jail capabilities gate mount and VFS operations.

## Major Entry Points

- `sys_jail()` validates privilege, copies jail versioned input, allocates a `struct prison`, copies IPv4/IPv6 address storage, copies hostname, applies default capabilities, and calls `kern_jail()`.
- `kern_jail()` looks up and stores the jail root path as `pr_root`, initializes varsym and IP caches, assigns a prison id, links the prison globally, creates per-jail sysctls, and attaches the current process.
- `sys_jail_attach()` validates privilege and attaches to an existing jail.
- `kern_jail_attach()` finds the prison, performs `kern_chroot(&pr->pr_root)`, holds the prison, atomically updates process credentials to point at the prison, sets `P_JAILED`, and applies restricted-root caps.
- `prison_hold()` and `prison_free()` manage prison references and final cleanup.
- `prison_priv_check()` decides whether a jailed credential may exercise a specific system capability.

## Jail Root and VFS Behavior

- Jail creation resolves `j->path` with `nlookup()` and stores a namecache handle in `pr->pr_root` via `cache_copy()`.
- Attach performs a chroot to the stored prison root.
- `sysctl_jail_list()` reports jail id, host, root path from `cache_fullpath()`, and jail IPs.
- `prison_free()` drops `pr_root` with `cache_drop()`.
- Default and per-jail capability bits include VFS-relevant controls: `vfs_chflags`, `vfs_mount_nullfs`, `vfs_mount_tmpfs`, `vfs_mount_devfs`, `vfs_mount_procfs`, and `vfs_mount_fusefs`.
- `prison_priv_check()` conditionally allows mount capabilities based on the prison's `pr_caps` bits and otherwise restricts sensitive root/network/jail operations.

## IP and Network Handling

- Supports legacy version 0 single IPv4 jails and DragonFly version 1 multi no-IP/IPv4/IPv6 jails.
- `prison_ipcache_init()` caches first loopback and non-loopback IPv4/IPv6 addresses.
- `prison_replace_wildcards()`, `prison_remote_ip()`, and `prison_local_ip()` translate loopback/wildcard behavior for jailed processes.
- `prison_get_nonlocal()` and `prison_get_local()` return cached addresses and optionally copy them into caller-provided sockaddr storage.
- `jailed_ip()` checks whether an address belongs to the prison.
- `prison_if()` restricts socket address families or IPs according to prison capabilities.

## Sysctl Surface

- Global defaults under `jail.defaults` define default prison capability bits.
- `jail.list` exposes active jail metadata to non-jailed callers.
- `jail.jailed` reports whether the current request credential is jailed.
- `prison_sysctl_create()` creates a per-jail node with mutable bits for system, network, and VFS mount capabilities; `prison_sysctl_done()` frees it.

## Synchronization

- `jail_lock` protects the global prison list, prison id assignment, jail count, and IP list scans.
- Prison references are atomically counted, with final list removal under `jail_lock`.
- Process credential updates occur under `p_token` and use `cratom_proc()` to avoid mutating shared credentials.

## Research Notes

- The jail root is held as a namecache handle rather than only a vnode/path string, which is relevant to namespace and chroot behavior.
- `prison_find()` returns a prison pointer after dropping `jail_lock`; callers that need lifetime stability must hold the prison. `kern_jail_attach()` calls it while outer `sys_jail_attach()` holds the same recursive-capable jail lock, then `prison_hold()` before publishing into credentials.
- The VFS mount capability matrix here is a primary policy hook for filesystem operations inside jails.
