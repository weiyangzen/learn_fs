# sources/user-network-fs/samba/source4/dsdb/repl/drepl_secret.c

Purpose: triggers targeted replication of a user's secret attributes, typically after authentication code asks for a missing/stale secret.

Important APIs/functions: `drepl_repl_secret()` parses the user DN, finds its NC root and local partition, chooses the first source DSA, builds a source DSA DN from its GUID, and calls `drepl_request_extended_op()` with `DRSUAPI_EXOP_REPL_SECRET` and the source high-watermark. `drepl_repl_secret_callback()` logs success, access denial (`WERR_DS_DRA_SECRETS_DENIED`), or other failure.

Control flow/state: the request is fire-and-forget from the IRPC trigger in `drepl_service.c`; the service sends no IRPC reply. All state is transient except for replicated object commits performed by the pull helper. Source choice is deliberately simple: the first source in the partition list.

Dependencies/integration: DREPL service partition/source state, DSDB NC-root lookup, GUID DNS naming, extended operation scheduler, and auth-triggered IRPC. Risks include arbitrary first-source selection, no direct caller result, failure when a partition has no sources, and secret/RODC partial attribute flag subtleties in lower layers. Test signals: invalid DN handling, no-source partition logging, denied-secret logging, min-USN/high-watermark passed into exop setup, and successful application of fetched secret attributes.
