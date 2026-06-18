# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_util.c

Purpose: contains shared NLM utilities for cookies/netobjs, lock/share parameter decoding, NLM-to-SAL status mapping, initialization, and granted-lock callback construction.

Important APIs/types/functions: exports `next_granted_cookie`, `lock_result_str`, `lock_end`, `fill_netobj`, `copy_netobj`, `netobj_free`, `netobj_to_string`, `nlm_init`, `free_grant_arg`, `nlm_process_parameters`, `nlm_process_share_parms`, `nlm_process_conflict`, `nlm_convert_state_error`, and `nlm_granted_callback`.

Control flow: parameter processors resolve NFSv3 file handles to FSAL objects, reject non-regular files and out-of-range offsets, look up NSM/NLM clients and owners according to `care_t`, obtain NLM state, build optional block data, and return either an NLM status or `-1` on success. Grant callback code adds a grant cookie, builds a `NLMPROC4_GRANTED_MSG`, schedules async work, and cancels the grant if scheduling fails.

State and persistence: initializes grace/cookie counters, creates/cancels grant cookie entries, allocates block data, and obtains client/owner/state refs. It mutates in-memory locking state indirectly through grant cookie management.

Dependencies and integration points: integrates `nfs3_FhandleToCache`, FSAL max-file-size, NSM monitor/client APIs, SAL state owner/state/cookie APIs, and NLM async sender.

Risks and test signals: ownership/ref cleanup in error branches is critical. Range overflow handling changes length to zero-to-EOF. `care_t` drives protocol semantics for missing owners. Test every lock/share caller with missing handles, non-regular objects, max-file-size edge cases, owner/client misses under each care mode, blocked lock grant success/failure, and conflict holder construction.
