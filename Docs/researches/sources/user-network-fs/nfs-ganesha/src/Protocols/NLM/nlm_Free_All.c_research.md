# sources/user-network-fs/nfs-ganesha/src/Protocols/NLM/nlm_Free_All.c

Purpose: implements NLM_FREE_ALL, releasing all locks for a named NSM client.

Important APIs/types/functions: exports `nlm4_Free_All` and `nlm4_Free_All_Free`. It uses `get_nsm_client`, `state_nlm_notify`, and `dec_nsm_client_ref`.

Control flow: it looks up the NSM client by name. If found, it invokes `state_nlm_notify(nsm_client, false, 0)`, which uses SM_NOTIFY-like cleanup semantics for that client, logs failures because the protocol result is void, releases the client reference, and returns `NFS_REQ_OK`.

State and persistence: mutates in-memory NLM lock state by releasing locks for a client. No result payload or persistent file metadata is written.

Dependencies and integration points: shares cleanup semantics with NSM notification handling and SAL lock ownership tracking.

Risks and test signals: no protocol error can be returned, so observability depends on logs. Test unknown clients, clients with active locks, clients rebooted with state protection, and state cleanup failure logging.
