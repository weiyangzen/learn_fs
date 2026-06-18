# sources/user-network-fs/nfs-ganesha/src/include/nlm_util.h

## Purpose
This header declares the NLM utility layer that translates wire-level NLM lock/share requests into Ganesha FSAL/SAL state objects and back into NLM status/conflict replies.

## Important APIs, Types, And Functions
Utility helpers include `lock_result_str()`, `copy_netobj()`, `netobj_free()`, and `netobj_to_string()`. `nlm_process_parameters()` is the central lock request normalizer: it consumes an RPC request, exclusivity flag, `nlm4_lock`, and NSM state, then fills a `fsal_lock_param_t`, target FSAL object, NSM client, NLM client, owner, optional blocked-lock callback data, and internal `state_t`. `nlm_process_share_parms()` performs analogous translation for share reservations. `nlm_process_conflict()` fills an `nlm4_holder` from an internal conflicting owner and lock range. `nlm_convert_state_error()` maps internal state-layer failures to `nlm4_stats`. `nlm_granted_callback()` is the state-layer hook used when a blocked lock can be granted.

## Control Flow
NLM service handlers call the process helpers before invoking the state manager. The helpers parse filehandles and owner handles, resolve exports/objects, acquire or create NSM/NLM client references and owner references, translate byte-range semantics, and optionally prepare callback data. After a state operation, handlers map internal statuses through `nlm_convert_state_error()` and report conflicts through `nlm_process_conflict()`.

## State And Persistence
This header does not store state directly, but its APIs manage references to SAL state objects. The returned NSM client, NLM client, state owner, blocked data, and state handle represent live server state and must be released according to the implementation's ownership contract. Netobj helpers allocate/copy/free byte buffers.

## Dependencies And Integration Points
It includes `gsh_list.h`, generated `nlm4.h`, and `sal_data.h`. It integrates NLM RPC handlers with FSAL object lookup, export state, SAL locking, blocked-lock callbacks, NSM monitoring, and generated NLM wire structures.

## Risks And Test Signals
Risks include reference leaks on partial failures, stale filehandle handling, incorrect owner identity composition, byte-range overflow for offset/length conversion, mismatched `care_t` behavior, and translating internal statuses to overly broad NLM failures. Test signals include lock/share requests for valid and stale handles, owner reuse, no-owner `care` cases, blocked-lock grant callbacks, conflict formatting, reclaim/grace handling, and netobj copy/free leak checks.
