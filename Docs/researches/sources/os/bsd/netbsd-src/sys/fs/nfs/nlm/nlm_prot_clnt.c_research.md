# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_clnt.c

This rpcgen-generated C file implements NLM client stubs. Each function wraps a single NLM/NSM RPC procedure by calling `CLNT_CALL_EXT()` with the procedure number, argument XDR routine, result XDR routine, RPC client handle, optional `rpc_callextra`, and timeout.

Key contents:
- Includes NetBSD kernel headers, `nlm_prot.h`, and RCS/provenance metadata.
- Implements `nlm_sm_notify_0()` for NSM notification RPCs.
- Implements NLM version 1 synchronous calls: `nlm_test_1()`, `nlm_lock_1()`, `nlm_cancel_1()`, `nlm_unlock_1()`, and `nlm_granted_1()`.
- Implements NLM version 1 asynchronous message calls and result calls, including test/lock/cancel/unlock/granted message and result variants.
- Implements NLM version 3 share/unshare, non-monitored lock, and free-all calls.
- Implements NLM version 4 synchronous calls, asynchronous message calls, result calls, share/unshare, non-monitored lock, and free-all calls.

Important behavior:
- The file contains no lock policy logic. It is transport glue generated from the NLM RPC definition.
- The `struct rpc_callextra *ext` argument lets callers attach auth, feedback callbacks, and other RPC metadata; `nlm_advlock.c` uses this for AUTH_UNIX credentials and lockd responsiveness feedback.
- Result freeing is the caller's responsibility via XDR free helpers where variable-length fields are returned.

Research notes:
- This is useful for tracing exact RPC procedure dispatch from implementation code to wire calls.
- Manual edits should be avoided; changes should come from the RPC protocol source and regeneration.
