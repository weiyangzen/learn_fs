# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/bindresvport.c

Read completely: 163 lines.

This file implements `bindresvport` and `bindresvport_sa`, binding sockets to privileged IP port ranges.

Key behavior: supports IPv4 and optionally IPv6. If caller passes `NULL`, it derives the socket family with `getsockname` and zeros a local sockaddr. If the port is zero, it temporarily switches the socket port-range option to low/reserved ports, calls `bind`, restores the old range on failure, and optionally returns the kernel-assigned address through `getsockname`.

Important interactions: used by RPC client creation (`clnt_tli_create`) for reserved-source-port behavior.

Security/reliability notes: requires kernel privilege/policy for reserved ports. The code manipulates per-socket port range options and must preserve `errno` across restoration attempts.
