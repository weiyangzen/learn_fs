# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Lock.c

Purpose: implements NLMv4 LOCK, NM_LOCK, and LOCK_MSG for byte-range locking.

Important APIs/types/functions: exports `nlm4_Lock`, `nlm4_Lock_Message`, and `nlm4_Lock_Free`; uses `nlm_process_parameters`, `state_lock`, `state_deleg_conflict`, `nfs_get_grace_status`, `nlm_convert_state_error`, async response helpers, and refcount release functions.

Control flow: it identifies monitored versus non-monitored lock variants, rejects missing exports, copies the cookie, gates reclaim/non-reclaim requests through grace handling unless FSAL handles grace, resolves object/client/owner/state/block data, checks NFSv4 delegation conflicts, increments anonymous operation tracking while locking, calls SAL `state_lock` under state lock, maps state outcomes, frees unused block data, and releases refs. The message variant schedules a LOCK_RES callback and drops the direct response.

State and persistence: creates or modifies in-memory NLM lock state and may enqueue blocking lock grant data. It does not write file data but enforces persistent client-visible lock behavior.

Dependencies and integration points: integrates FSAL max-file-size limits, NSM monitoring, NLM owner/client tables, SAL locking, NFS grace state, and async callbacks.

Risks and test signals: range overflow conversion, delegation conflict drop, grace/reclaim behavior, blocked lock cleanup, and reference release are high-risk. Test blocking/nonblocking locks, NM_LOCK, reclaim during grace, lock past max file size, delegation conflict, async message response, and denied/no-locks cases.
