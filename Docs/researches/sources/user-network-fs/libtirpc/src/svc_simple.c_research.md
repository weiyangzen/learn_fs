<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_simple.c -->
# sources/user-network-fs/libtirpc/src/svc_simple.c

Purpose: simplified `rpc_reg()` front end that lets applications register procedure callbacks without building full dispatch functions.

Important APIs and functions: `rpc_reg()` registers one program/version/procedure on transports selected by a nettype. Static `universal()` is the shared dispatch routine for all simplified registrations.

Control flow: `rpc_reg()` rejects `NULLPROC`, selects `netpath` by default, iterates matching netconfigs, reuses an existing transport/xdr buffer by netid or creates one with `svc_tli_create`, computes receive size, allocates a per-netid decode buffer and netid string, avoids duplicate rpcbind unsets when the program/version/netid is already registered, registers `universal()` through `svc_reg`, and prepends a `proglst` entry. `universal()` handles NULLPROC by replying void, otherwise finds the exact program/version/procedure/netid entry, zeroes the shared XDR buffer, decodes arguments, calls the user callback, sends the encoded result, and frees decoded args.

State and persistence: static `proglst` linked list persists process-wide and is protected by `proglst_lock`. Each netid can share one transport and one argument buffer among simplified registrations.

Dependencies and integration points: built on `__rpc_setconf`, `svc_tli_create`, `svc_reg`, `svc_getargs`, `svc_sendreply`, and `svc_freeargs`. Legacy `registerrpc()` in `rpc_soc.c` delegates here for UDP.

Risks: `universal()` holds `proglst_lock` while decoding, invoking user code, replying, and freeing args, so callbacks that call registration APIs can deadlock and unrelated simplified procedures are serialized. It calls `memset(xdrbuf, 0, sizeof(pl->p_recvsz))`, which clears only the size of the integer field rather than the receive buffer, leaving stale argument bytes risk. Shared per-netid argument buffers are not safe for concurrent dispatch.

Test signals: registering multiple procedures on one transport, NULLPROC response, duplicate program/version/netid handling, decode failure path, void and non-void result behavior, callback returning null for non-void, concurrent requests on same netid, and regression for full-buffer zeroing/stale arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_simple.c -->
