# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/nlm/nlm_prot_server.c

Provides the RPC service implementation stubs for NLM protocol versions 0, 1, 3, and 4. The file mostly adapts older NLM structures and procedure numbers to the NLMv4 internal implementation in `nlm_prot_impl.c`.

The conversion helpers map legacy `nlm_lock`, `nlm_share`, `nlm_holder`, and result/status structures to their `nlm4_*` equivalents and back. Version 1 and version 3 procedures call the version 4 service helpers after conversion; version 3 adds share/unshare, non-monitored lock, and free-all wrappers.

Synchronous procedures return direct test/lock/cancel/unlock/granted results. Asynchronous `_MSG` procedures run the same operation, then send the matching `_RES` callback over a `CLIENT *` returned by the implementation layer. Most incoming `_RES` procedures are effectively ignored, except `nlm4_granted_res_4_svc()`, which calls `nlm_do_granted_res()` to complete an async server-side granted lock.

Share and unshare are not implemented as real share reservations: `nlm4_share_4_svc()` and `nlm4_unshare_4_svc()` zero the result and return denied. `nlm4_nm_lock_4_svc()` runs `nlm_do_lock()` with monitoring disabled. Result cleanup delegates to `xdr_free()`.
