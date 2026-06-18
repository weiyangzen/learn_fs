# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_generic.c

Read completely: 400 lines.

This file implements generic RPC client creation: `clnt_create_vers`, `clnt_create`, `clnt_tp_create`, `clnt_tli_create`, and `__clnt_sigfillset`.

Key behavior: `clnt_create` iterates netconfig entries for a requested nettype and tries `clnt_tp_create`, preserving more specific errors than name-to-address translation failures. `clnt_tp_create` asks rpcbind for the service address and either reuses a returned client or creates a new one. `clnt_tli_create` opens/binds a socket when needed, chooses `clnt_vc_create` for ordered connection transports or `clnt_dg_create` for datagrams, records netid/device strings, and marks library-created fds close-on-destroy. `clnt_create_vers` probes NULLPROC to negotiate a supported version range.

Important interactions: central dispatcher for RPC client setup; bridges netconfig/rpcbind address lookup to datagram and virtual-circuit implementations.

Security/reliability notes: connection creation may bind reserved ports. `__clnt_sigfillset` blocks most signals during critical client sections but deliberately leaves interactive termination signals unblocked.
