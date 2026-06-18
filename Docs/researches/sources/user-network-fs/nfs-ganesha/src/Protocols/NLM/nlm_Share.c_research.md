# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Share.c

Purpose: implements NLMv4 SHARE, creating DOS-style share reservations for NFSv3 clients.

Important APIs/types/functions: exports `nlm4_Share` and `nlm4_Share_Free`; uses `nfs_param.core_param.disable_NLM_SHARE`, `nlm_process_share_parms`, `state_nlm_share`, `check_and_remove_conflicting_client`, grace handling, and netobj helpers.

Control flow: it optionally fails all share calls if disabled, rejects missing exports, logs file handle/owner/access/deny details, copies the cookie, handles grace/reclaim admission, resolves object/client/owner/share state, calls `state_nlm_share`, retries once after removing expired conflicting clients on denial, maps state errors, and releases refs.

State and persistence: creates or updates in-memory NLM share reservation state. No file metadata is persisted, but access denial semantics become visible to other clients.

Dependencies and integration points: ties NLM share wire structures to SAL share state, NSM/NLM client management, export grace support, and global NFS configuration.

Risks and test signals: disabled-share behavior, reclaim gating, expired-client conflict removal, and cleanup after `nlm_process_share_parms` errors need coverage. Test read/write/deny combinations, conflict/expired client retry, grace reclaim/non-reclaim, non-regular files, and cookie free paths.
