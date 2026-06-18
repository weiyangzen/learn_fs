# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Cancel.c

Purpose: implements NLMv4 CANCEL and CANCEL_MSG, canceling a blocked range lock request.

Important APIs/types/functions: exports `nlm4_Cancel`, `nlm4_Cancel_Message`, and `nlm4_Cancel_Free`; uses `nlm_process_parameters`, `state_cancel`, `nlm_convert_state_error`, async scheduling helpers, and netobj cookie copy/free helpers.

Control flow: it rejects missing exports as `NLM4_STALE_FH`, copies the cookie, checks grace-period state, resolves the FSAL object/NLM owner/client without requiring owner existence, calls `state_cancel`, maps state errors, and releases refs. The message variant obtains non-monitoring clients, invokes the synchronous function, schedules an async CANCEL_RES, then always drops the original RPC response.

State and persistence: cancels in-memory blocked lock state in SAL/state. It does not directly persist data but affects pending lock queues and grant callbacks.

Dependencies and integration points: depends on NLM utility parameter decoding, SAL state cancellation, NSM/NLM client reference management, and `nlm_async.c` callback transport.

Risks and test signals: the file uses `res_nlm4test.cookie` in some places while sending `res_nlm4`, so cookie union consistency should be tested. Test cancellation during grace, missing owner/client, stale handles, async message response failure, and block queue cleanup.
