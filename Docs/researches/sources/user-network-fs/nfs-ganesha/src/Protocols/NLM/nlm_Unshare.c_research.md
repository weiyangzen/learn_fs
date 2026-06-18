# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Unshare.c

Purpose: implements NLMv4 UNSHARE, removing a share reservation.

Important APIs/types/functions: exports `nlm4_Unshare` and `nlm4_Unshare_Free`; uses `disable_NLM_SHARE`, `nlm_process_share_parms`, `state_nlm_share(..., unshare=true)`, netobj cookie helpers, and reference release helpers.

Control flow: it optionally fails when share support is disabled, rejects missing exports, logs details, copies the cookie, resolves object/client/owner/share state with `CARE_NOT`, invokes `state_nlm_share` in unshare mode, maps errors to NLM statuses, releases refs, and returns `NFS_REQ_OK`.

State and persistence: removes or updates in-memory share reservations. Missing client/owner under `CARE_NOT` is treated as granted because there is nothing to remove.

Dependencies and integration points: pairs with `nlm_Share.c` and the SAL share state machine.

Risks and test signals: unlike SHARE, this does not do grace handling. Test unshare existing and nonexistent shares, disabled share config, non-regular files, stale handles, denied state errors, and cookie cleanup.
