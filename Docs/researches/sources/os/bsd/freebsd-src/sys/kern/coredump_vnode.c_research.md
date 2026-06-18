# File Research: sources/os/bsd/freebsd-src/sys/kern/coredump_vnode.c

## Summary
Implements the traditional vnode-backed coredumper. It expands `kern.corefile`, opens and validates the target file, serializes writers, invokes the process ABI's coredump routine through a `coredump_writer`, and optionally sends devctl notifications.

## Main Responsibilities
- Registers `vnode_coredumper` at `SI_SUB_EXEC`.
- Exposes sysctls/tunables for core naming, indexed core rotation, capability-mode core dumps, NODUMP flagging, and devctl notifications.
- Implements vnode writer callbacks `core_vn_write()` and `core_vn_extend()`.
- Expands core filename templates using process name, pid, uid, signal, hostname, and optional `%I` index.
- Creates, rotates, truncates, locks, writes, and closes core files.

## Key APIs
- `corefile_open()` expands `kern.corefile`, appends compression suffixes, and opens the target vnode.
- `corefile_open_last()` implements `%I` rotation by finding an unused core filename or the oldest existing one.
- `coredump_vnode()` is the registered coredumper handler.
- `core_vn_write()` writes core payload through `vn_rdwr_inchunks()` with direct and range-locked I/O.
- `core_vn_extend()` extends/truncates the vnode under a write transaction.

## Important Behavior
Core files are created with `O_CREAT | FWRITE | O_NOFOLLOW`; setuid/setgid processes use `O_EXCL` in the non-indexed path. The target must be a regular file, have one link, not be a system vnode, and be owned by the effective user.

Before writing, the code takes a full-file vnode range lock and attempts an advisory write lock. It truncates the file to zero, optionally sets `UF_NODUMP`, marks `ACORE`, and then calls `p->p_sysent->sv_coredump()`.

When `kern.coredump_devctl` is enabled and writing succeeds, the code emits a quoted devctl event containing executable path, core path, jail id, pid, parent pid, and signal.

## State and Synchronization
`corefilename` is protected by `allproc_lock`. Core writing uses vnode locks, vnode range locks, optional advisory locks, and mount write transactions for extension/truncation.

## Risks
The file-name formatter is security-sensitive because it expands kernel-controlled paths into vnode opens. The code avoids following symlinks and validates ownership/link count/type, but changes to this area can easily weaken corefile safety.
