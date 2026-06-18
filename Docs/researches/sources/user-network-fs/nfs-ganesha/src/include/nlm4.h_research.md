# sources/user-network-fs/nfs-ganesha/src/include/nlm4.h

## Purpose
This rpcgen header defines the Network Lock Manager version 4 protocol surface used by Ganesha for NFSv3-style advisory locking and share reservations. It provides the XDR data model, RPC procedure numbers, client/server stub prototypes, and XDR function declarations for program 100021 version 4.

## Important APIs, Types, And Functions
Important constants include string/object size caps (`LM_MAXSTRLEN`, `MAXNETOBJ_SZ`, `SM_PRIV_SZ`), `NLMPROG`, `NLM4_VERS`, `NLMPROC4_*`, and `NLM_V4_NB_OPERATION`. `nlm4_stats` captures granted, denied, grace-period, deadlock, read-only filesystem, stale filehandle, file-too-large, and generic failure states. Core protocol structures are `nlm4_res`, `nlm4_testres`, `nlm4_holder`, `nlm4_lock`, lock/test/cancel/unlock argument structs, share mode/access enums, `nlm4_shareargs`, `nlm4_shareres`, `nlm4_free_allargs`, and `nlm4_sm_notifyargs`.

The header declares sync RPC entry points such as `nlmproc4_test_4`, `nlmproc4_lock_4`, `nlmproc4_cancel_4`, `nlmproc4_unlock_4`, and service-side `_svc` variants. It also declares async message/result procedures (`*_MSG`, `*_RES`), `NLMPROC4_SM_NOTIFY`, share/unshare, no-monitor lock, free-all, `nlmprog_4_freeresult`, and XDR functions for every exported structure.

## Control Flow
NLM control flow is encoded as independent RPC procedures. Synchronous calls return `nlm4_res`, `nlm4_testres`, or `nlm4_shareres`; asynchronous calls send a void request and later deliver a result through matching `*_RES` procedures keyed by cookies. Test replies use a discriminated union: when status indicates denial, `nlm4_holder` describes the blocking lock. Share procedures carry an extra sequence value in results. `SM_NOTIFY` bridges status monitor restart notifications into the lock manager.

## State And Persistence
The header defines wire state rather than owning storage. Cookies correlate async requests and results. `nlm4_lock` carries caller name, filehandle, owner handle, svid, offset, and length. Reclaim/state fields link locks to NSM restart state. Actual persistent lock/share/client ownership lives in SAL/state-management code outside this generated header.

## Dependencies And Integration Points
It depends on `gsh_rpc.h` for RPC/XDR types including `CLIENT`, `SVCXPRT`, `XDR`, `netobj`, and `struct svc_req`. It integrates with NLM service dispatch, NLM client callbacks, NSM monitor notifications, SAL lock owner/client tracking, and utility code in `nlm_util.h`/`nlm_async.h`.

## Risks And Test Signals
Risks include ABI drift from rpcgen output, duplicate typedefs for fixed-width integer names, cookie/owner byte ownership, and status mapping mismatches between NLM and internal state codes. Async procedures need timeout and duplicate-response coverage. Test signals include XDR round trips for every argument/result struct, lock/test/unlock/cancel integration tests, share/unshare tests, reclaim-after-grace tests, SM_NOTIFY restart simulations, and interop with Linux `lockd` clients.
