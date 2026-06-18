# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_perror.c

Read completely: 324 lines.

This file implements RPC client error string and printing helpers: `clnt_sperror`, `clnt_perror`, `clnt_sperrno`, `clnt_perrno`, `clnt_spcreateerror`, `clnt_pcreateerror`, and authentication-error text mapping.

Key behavior: formats `struct rpc_err` status with errno, version ranges, or auth failure details where applicable. Creation errors use global `rpc_createerr` and append lower-level portmapper/system details for selected statuses.

Important interactions: used by callers and tools to report errors from all RPC client transports.

Security/reliability notes: uses a single malloc-backed static buffer resized only by initial assignment to 256 bytes, so returned strings are not thread-safe and can truncate through `snprintf`/`strncat` length handling.
