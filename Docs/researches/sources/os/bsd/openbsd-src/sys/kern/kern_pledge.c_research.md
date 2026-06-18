# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_pledge.c

Purpose: Implements OpenBSD `pledge(2)` promise parsing and runtime enforcement across syscalls, path lookup, file descriptor passing, sysctl, ioctl, sockets, socket options, and selected helpers.

Key behavior:
- Defines `pledge_syscalls[]`, mapping each syscall to required promise bits or `PLEDGE_ALWAYS`.
- Parses promise strings through sorted `pledgereq[]` and `pledgereq_flags()`.
- `sys_pledge()` only permits promise reduction, supports exec promises, and destroys unveil state when path-related promises are dropped.
- `pledge_syscall()` snapshots per-process promises into the thread and rejects missing syscall promises.
- `pledge_fail()` either returns `ENOSYS` in `error` mode or logs, marks accounting, stops sibling threads, and forces `SIGABRT`.

Filesystem and path relevance:
- `pledge_namei()` is the central filesystem gate. It checks `ni_pledge` against current promises, handles `exec`, `rpath`, `wpath`, `cpath`, `dpath`, and delegates unveil checks to `namei()`.
- `__pledge_open()` paths receive special handling for fixed libc/service files such as `/dev/null`, `/etc/resolv.conf`, `/etc/hosts`, password databases, and zoneinfo.
- File descriptor passing rejects directory vnode descriptors while allowing sockets, pipes, dmabuf, sync objects, and non-directory vnodes.

Security and device filtering:
- `pledge_sysctl()` whitelists read-only MIBs by promise category.
- `pledge_ioctl()` contains narrow allowlists for tty, disklabel, audio, video, DRM, PF, BPF, VMM, PSP, tape, route, and write-route operations.
- `pledge_sockopt()` separates always-safe options, DNS resolver options, routing table changes, multicast options, and general inet/unix permissions.
- Helper checks cover `chown`, `adjtime`, `sendto`, `socket`, `flock`, `swapctl`, `fcntl(F_SETOWN)`, `kill`, and executable mappings after `kbind`.

Important dependencies:
- VFS/namei: `struct nameidata`, `BYPASSUNVEIL`, vnode/file types.
- Process state: `ps_pledge`, `ps_execpledge`, `PS_PLEDGE`, `PS_EXECPLEDGE`.
- Signal path: violations call `sigabort()` and may use `single_thread_set()`.
