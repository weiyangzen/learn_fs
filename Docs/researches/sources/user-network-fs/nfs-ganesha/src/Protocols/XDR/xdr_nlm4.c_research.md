# sources/user-network-fs/nfs-ganesha/src/Protocols/XDR/xdr_nlm4.c

Purpose: rpcgen-style XDR implementation for NLMv4 lock manager protocol structures: status/results, lock descriptors, test replies, lock/cancel/test/unlock arguments, share reservations, free-all requests, and NSM notify arguments used by locking recovery.

Important APIs and types: `xdr_nlm4_stats()`, `xdr_nlm4_stat()`, `xdr_nlm4_res()`, `xdr_nlm4_holder()`, `xdr_nlm4_testrply()`, `xdr_nlm4_testres()`, `xdr_nlm4_lock()`, `xdr_nlm4_lockargs()`, `xdr_nlm4_cancargs()`, `xdr_nlm4_testargs()`, `xdr_nlm4_unlockargs()`, `xdr_nlm4_share()`, `xdr_nlm4_shareargs()`, `xdr_nlm4_shareres()`, `xdr_nlm4_free_allargs()`, and `xdr_nlm4_sm_notifyargs()`.

Control flow: routines serialize fields in NLM protocol order. `xdr_nlm4_testrply()` switches on status and only includes `nlm4_holder` when the test is denied. Lock and share structures include caller names, file handles and owner handles as netobjs, process id, offsets, lengths, modes, and access masks.

State and persistence: no local state. Decode/free state is owned by XDR netobj/string allocation and the caller.

Dependencies and integration points: includes `nlm4.h` and `nfs_fh.h`; used by NLM dispatch and recovery code when serializing network lock manager traffic. It is conditionally relevant when NLM support is enabled in the build.

Risks: bounded strings use `LM_MAXSTRLEN`, `LM_MAXNAMELEN`, and `SM_MAXSTRLEN`; malformed or oversized caller names must fail cleanly. Netobj sizes are delegated to `xdr_netobj()`, so upstream limits matter for memory pressure. Offsets and lengths are 64-bit and should be validated by lock logic after decode.

Test signals: round-trip all NLMv4 request/response forms, denied test replies with holder data, free-all and notify arguments, oversized strings/netobjs, and XDR_FREE for decoded variable fields.
