# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_private.h

Read completely: 32 lines.

This private resolver header defines `struct __res_state_ext`, holding full-size nameserver sockaddr storage, sort-list entries, IPv6 reverse lookup suffixes, `resolv.conf` mtime, kqueue fd, config fd, and kqueue owner pid.

It also declares private resolver functions: `res_ourserver_p`, `__res_vinit`, and compatibility state accessors under `COMPAT__RES`.

Important interactions: shared by `res_init.c` and `res_send.c`; the extension bridges old ABI fields such as `nsaddr_list` with IPv6-capable resolver internals.

Security/reliability notes: no logic here, but ABI compatibility depends on keeping this extension private and preserving legacy `struct __res_state` layout expectations.
