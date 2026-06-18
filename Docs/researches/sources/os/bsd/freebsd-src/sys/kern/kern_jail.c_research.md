# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_jail.c

## Purpose
Implements FreeBSD jail core: jail creation, update, lookup, removal, attachment, hierarchy/lifetime rules, jail parameters/sysctls, IP and VNET restrictions, credential confinement checks, privilege policy, process linkage, RACCT integration, and DDB inspection.

## Main Elements
- Defines `prison0`, global jail lists/locks (`allprison`, `allprison_lock`), jail ID allocation state, default allow/statfs/devfs settings, and parameter flag tables.
- `prison0_init()` completes host jail initialization, including cpuset, OS release values, MAC label setup, and optional preloaded host UUID validation.
- Legacy `jail(2)` compatibility is translated into the `jail_set(2)` iovec option model by `kern_jail()`.
- `kern_jail_set()` is the central create/update implementation. It parses options, validates permissions and descriptor modes, resolves paths, handles JID/name lookup, creates or updates `struct prison`, applies host/IP/allow/statfs/devfs parameters, invokes jail OSD methods, optionally attaches the caller, and returns descriptors/errors to user space.
- IP support uses epoch-safe `struct prison_ip` buffers, primary-address-preserving sorting, duplicate/validity checks, parent-subset checks, conflict checks, descendant restriction, and deferred freeing via `NET_EPOCH_CALL`.
- `kern_jail_get()` implements parameter retrieval by descriptor, lastjid, jid, or name, including descriptor return, MAC checks, module parameters, and user copyout.
- `sys_jail_remove()`, `sys_jail_remove_jd()`, `prison_remove()`, `sys_jail_attach()`, and `sys_jail_attach_jd()` implement removal and attachment entry points.
- `do_jail_attach()` updates cpuset, root/current directory, credentials, process jail list linkage, OSD attach hooks, knotes, and MAC notifications.
- Lookup helpers (`prison_find`, `prison_find_child`, `prison_find_name`) enforce hierarchy visibility under `allprison_lock`.
- Reference/lifetime routines split structural refs (`pr_ref`) from user refs (`pr_uref`) and use a `jail_remove` taskqueue to complete teardown outside unsafe contexts.
- `prison_deref()` and `prison_deref_kill()` transition jails to dying/invalid, kill descendant processes, detach descriptors, call module remove hooks, release VNETs, roots, IP lists, cpusets, OSD, RACCT, and memory.
- Confinement helpers implement address-family checks, IP ownership checks, NFS daemon allowance, parent/child visibility, hostname/domain/UUID/hostid accessors, mount visibility/statfs rewriting, and VNET ownership tests.
- `prison_priv_check()` is the jail privilege policy switch, granting or denying individual privileges based on jail state and `allow.*` bits.
- Sysctls expose jail listing, jailed/vnet state, deprecated defaults, child counters, parameter descriptions, allow flags, and dynamic `allow.mount.<fs>` flags.
- RACCT code maps jail names to shared resource accounting buckets and handles rename migration.
- DDB support dumps prison structure state, flags, allow bits, and IP lists.

## Dependencies And Integration
Integrates with VFS options and path lookup, vnode roots/chroot, MAC framework, cpuset, credentials, process lists, VNET, network epoch, OSD jail methods, descriptor support from `kern_jaildesc.c`, metadata methods from `kern_jailmeta.c`, RACCT/RCTL, kqueue notes, sysctl jail parameters, devfs/statfs policy, and network address-family helpers.

## Risk Notes
The file is security-critical. Correctness depends on preserving jail hierarchy visibility, parent-imposed restrictions, immutable creation-time properties (`vnet`, IP mode, path, OS release), and lock ordering among `allprison_lock`, prison mutexes, allproc, vnode, and descriptor locks. IP lists are read by network fast paths and must remain epoch-safe. Reference accounting is subtle because persistent jails, attached processes, descriptors, and removal all hold different references.
