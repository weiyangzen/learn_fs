# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_domain.c

Network protocol-domain registry and dispatcher.

This file defines the kernel's static `domains[]` table, conditionally including MPLS, PF_KEY, IPv6, frame, and always including IPv4, UNIX, and route domains. `domaininit()` runs each domain initializer and protocol initializer, enforces a minimum `max_linkhdr` of 64 bytes for tunnel header headroom, computes `max_hdr`, and starts fast and slow protocol timer callbacks.

Protocol lookup helpers search the domain table and each domain's `protosw` range. `pffinddomain()` returns a family match, `pffindtype()` returns a socket type match, and `pffindproto()` matches family/protocol/type with a raw-socket fallback to protocol zero. These are used by socket creation and protocol-control paths.

`net_sysctl()` dispatches `net.*` sysctl requests. It has direct dispatch for link queues, UNIX-domain sysctls, BPF, pflow, PIPEX, and MPLS when configured, then falls back to per-protocol `pr_sysctl`. For protocols without `PR_MPSYSCTL`, it locks the userspace output buffer with `sysctl_vslock()` around the protocol handler.

`pfctlinput()` broadcasts control-input notifications to all protocol switch entries while asserting the network lock. `pffasttimo()` and `pfslowtimo()` walk every protocol and invoke configured timer hooks, rescheduling at 200 ms and 500 ms respectively.

Notable constraints: protocol/domain registration is compile-time static; sysctl names are treated as nonterminal at the network family level; and timer callbacks are run from timeout context with the protocol hook responsible for its own locking discipline.
