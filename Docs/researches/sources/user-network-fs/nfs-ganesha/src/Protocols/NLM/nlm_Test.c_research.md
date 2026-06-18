# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Test.c

Purpose: implements NLMv4 TEST and TEST_MSG, checking whether a proposed byte-range lock would conflict.

Important APIs/types/functions: exports `nlm4_Test`, `nlm4_Test_Message`, and `nlm4_Test_Free`; uses `nlm_process_parameters`, `state_test`, `nlm_process_conflict`, `nlm_convert_state_error`, async test response helpers, and holder netobj cleanup.

Control flow: it rejects missing exports, copies the cookie, checks grace status, resolves lock parameters with owner care, calls `state_test`, fills conflict holder details on `STATE_LOCK_CONFLICT`, releases state/client/owner/object refs, and returns the lock test status. The message variant schedules TEST_RES asynchronously and drops the direct response.

State and persistence: reads lock state and may take temporary state/owner references. It should not create persistent locks, though helper lookup can create/return NLM state depending on care semantics.

Dependencies and integration points: bridges NLM test requests to SAL lock conflict reporting and uses async callback infrastructure for message procedures.

Risks and test signals: conflict holder ownership and `oh` allocation/free are critical. Test granted/no-conflict, denied with holder, grace period denial, stale handles, unknown owners, async TEST_MSG, and holder cleanup in `nlm4_Test_Free`.
