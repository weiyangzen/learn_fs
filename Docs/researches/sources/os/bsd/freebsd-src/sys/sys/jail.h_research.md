# File Research: sources/os/bsd/freebsd-src/sys/sys/jail.h

Defines the FreeBSD jail public ABI and kernel prison internals. Userland structures include `struct jail` API version 2, `struct xprison` version 3, jail states, and flags for create/update/attach/get/remove/descriptor behavior. Userland functions include `jail`, `jail_set`, `jail_get`, attach/remove variants, and descriptor attach/remove variants.

Kernel/private sections define `struct prison`, the central jail object with all-prison tree links, process list, parent/children, mutex, OSD, cpuset, VNET, root vnode, IP restrictions, RACCT proxy, MAC label, jail descriptors, child limits, allow flags, securelevel, statfs/devfs policy, lifecycle state, host identity strings, OS release/date, and refcounts.

It defines jail flags for persistence, hostname virtualization, IPv4/IPv6 restrictions, VNET, source-address selection, and removal/internal state. Allow flags cover hostname, SysV IPC, raw sockets, mount, quotas, socket address families, mlock, msgbuf, debugging, superuser-like checks, reserved ports, NFSD, extattr, time adjustment, routing, parent tamper, and audit.

The header also provides prison traversal macros, jail sysctl parameter declaration macros, and a broad kernel API for lookup, reference management, process linking, removal, IP checks, address-family checks, privilege checks, statfs enforcement, VFS allow registration, and RACCT iteration.
