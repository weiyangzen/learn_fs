# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unlock.c

Purpose: implements NLMv4 UNLOCK and UNLOCK_MSG for releasing byte-range locks.

Important APIs/types/functions: exports `nlm4_Unlock`, `nlm4_Unlock_Message`, and `nlm4_Unlock_Free`; uses `nlm_process_parameters` with `CARE_NOT`, `state_unlock`, `nlm_convert_state_error`, async unlock response helpers, and netobj free.

Control flow: it rejects missing exports, copies the cookie, resolves object/client/owner/state without requiring existing owner/client, treats missing state as success, calls `state_unlock` when state exists, maps errors, releases state/client/owner/object refs, and returns success. The message handler sends an async UNLOCK_RES and drops the direct RPC reply.

State and persistence: mutates in-memory lock state by releasing locks. No persistent file data is written.

Dependencies and integration points: uses common NLM parameter conversion, SAL unlock, NSM/NLM client tracking, and async callback transport.

Risks and test signals: success-on-missing-owner/client is protocol-significant. Test unlock existing and nonexistent locks, missing client/owner, stale file handle, non-regular files, async response failure, and cleanup of copied cookies.
