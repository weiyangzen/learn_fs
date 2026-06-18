# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Granted_Res.c

Purpose: handles client replies to server-initiated `NLMPROC4_GRANTED_MSG` callbacks for previously blocked locks.

Important APIs/types/functions: exports `nlm4_Granted_Res` and `nlm4_Granted_Res_Free`; uses `state_find_grant`, `state_release_grant`, `state_complete_grant`, `nlm_signal_async_resp`, export reference/context setup, and `export_ready`.

Control flow: it decodes/logs the cookie, finds the pending grant cookie entry, ignores old replies with missing entries or block data, installs the related export into `op_ctx`, and either releases the grant on client error/stale export or completes it and signals the async sender waiting for the acknowledgement.

State and persistence: updates in-memory grant cookie/blocking-lock state. It may complete or release a pending lock grant, changing subsequent lock availability.

Dependencies and integration points: pairs with `nlm_granted_callback` and `nlm_send_async`; depends on export lifetime management and the state cookie table.

Risks and test signals: stale exports, duplicate/old replies, missing block data, and failed release paths are important. Test successful grant acknowledgement, denied grant response, stale export cleanup, old cookie ignore, and async wait signalling.
