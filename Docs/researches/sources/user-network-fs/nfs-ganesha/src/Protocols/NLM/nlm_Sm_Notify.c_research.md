# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Sm_Notify.c

Purpose: handles incoming NSM `SM_NOTIFY` callbacks delivered through the NLM program when monitored clients reboot.

Important APIs/types/functions: exports `nlm4_Sm_Notify` and `nlm4_Sm_Notify_Free`; uses `is_loopback`, `get_nsm_client`, `state_nlm_notify`, `set_op_context_client`, `SetClientIP`, and op context caller/client restoration.

Control flow: only loopback callers are honored. The handler temporarily clears client/caller context so the NSM client is looked up by caller name, restores the matched Ganesha client for cleanup, calls `state_nlm_notify(nsm_client, true, state)`, releases the NSM client, then restores original op context values.

State and persistence: mutates in-memory lock/share state by removing or protecting state according to the reboot state number. No result payload is returned.

Dependencies and integration points: integrates local statd notification delivery with NLM state cleanup and request context bookkeeping.

Risks and test signals: loopback validation, op context restoration, caller-name mapping, and cleanup semantics are important. Test spoofed non-loopback notify, known/unknown clients, reboot state protection, and restoration when original client is null or changed.
