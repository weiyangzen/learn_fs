# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_init.c

Read completely: 960 lines.

This file initializes, reloads, and destroys resolver state. Public/internal entry points include `res_ninit`, `__res_vinit`, `res_check`, `res_nclose`, `res_ndestroy`, `res_get_nibblesuffix`, `res_get_nibblesuffix2`, `res_setservers`, `res_getservers`, plus random-ID helpers `res_rndinit` and `res_nrandomid`.

Key behavior: `__res_vinit` sets defaults, allocates `__res_state_ext`, seeds random state, installs default IPv4/IPv6 nameservers, parses `LOCALDOMAIN`, `/etc/resolv.conf`, and `RES_OPTIONS`, builds search lists, sort lists, nameserver arrays, IPv6 reverse suffixes, and kqueue monitoring state. `res_check` uses saved `resolv.conf` mtime and a vnode kqueue to reinitialize on config changes. `res_nclose` closes TCP and per-server UDP sockets; `res_ndestroy` also closes kqueue/config fds and frees extension/random allocations.

Important interactions: `res_send.c` calls `res_check` and consumes server/socket fields; `res_query.c` depends on search-list/options fields; `res_private.h` defines the extension object. The file uses MD5 over time/pid seed material to generate 16-bit DNS IDs.

Security/reliability notes: environment-controlled `LOCALDOMAIN`, `RES_OPTIONS`, and `HOSTALIASES` behavior is inherited resolver API surface. Allocation failure for the extension is deliberately deferred through `h_errno`, leaving a partially useful state. `res_setservers` closes existing sockets before replacing server addresses, so callers must expect connection cache invalidation.
