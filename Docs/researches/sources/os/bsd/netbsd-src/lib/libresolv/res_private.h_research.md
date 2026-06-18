# File Research: sources/os/bsd/netbsd-src/lib/libresolv/res_private.h

Read completely: 24 lines.

Defines the private resolver extension structure `__res_state_ext`, containing extended nameserver addresses, resolver sort-list entries for IPv4/IPv6 address/mask pairs, and two suffix buffers. It also declares `res_ourserver_p()`.

This header is a small bridge for code that needs resolver internals beyond the public `res_state` surface.
