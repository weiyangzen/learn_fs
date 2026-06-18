# sources/user-network-fs/libtirpc/tirpc/rpc/clnt.h

Purpose: `clnt.h` defines the client-side RPC handle ABI, error structures, control operations, creation APIs, simplified RPC calls, and broadcast APIs.

Important APIs, types, and functions: Key types are `struct rpc_err`, `CLIENT`, `struct clnt_ops`, `struct rpc_timers`, `struct rpc_createerr`, and `resultproc_t`. Macros dispatch `CLNT_CALL`, `CLNT_ABORT`, `CLNT_GETERR`, `CLNT_FREERES`, `CLNT_CONTROL`, and `CLNT_DESTROY`. Constructors include generic nettype/netconfig creators, version-negotiating creators, `clnt_vc_create`, `clnt_dg_create`, raw/unix compatibility creators, error printers, `rpc_call`, `rpc_broadcast`, and `rpc_broadcast_exp`.

Control flow: Applications create a `CLIENT`, install/use an `AUTH`, call remote procedures through the vtable with XDR argument/result filters and timeout, inspect errors, free decoded results, control transport options, then destroy the handle. Generic creators resolve netconfig/rpcbind addresses and select connection-oriented or datagram transports.

State and persistence behavior: A `CLIENT` persists authenticator, transport-private state, netid, and transport provider strings. Global creation error state is exposed through `__rpc_createerr`.

Dependencies and integration points: It depends on `auth.h`, `clnt_stat.h`, `netconfig.h`, and Unix socket types. It is the central include for client transports, rpcbind clients, broadcast code, and GSS authentication.

Risks: Vtable macros lack null checks. Global `rpc_createerr` can be thread-sensitive depending on implementation. Control request numbers are ABI and transport-specific; unsupported controls must fail predictably. Broadcast callbacks are varargs-compatible and require careful type discipline.

Test signals: Tests should cover all creation paths, version negotiation, timeout/retry controls, fd close/no-close controls, auth refresh on `RPC_AUTHERROR`, error string generation, broadcast early-stop callbacks, and unrecoverable-status classification.
