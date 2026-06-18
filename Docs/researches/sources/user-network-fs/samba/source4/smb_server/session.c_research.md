# Research: sources/user-network-fs/samba/source4/smb_server/session.c

Purpose: manages authenticated SMB session IDs (VUIDs) and their lifecycle on a server connection.

Important APIs: `smbsrv_init_sessions()` initializes the session idtree and list with a masked 24-bit limit. `smbsrv_session_find()` validates VUID, checks the idtree, returns only sessions with `session_info`, and updates `last_request_time`. `smbsrv_session_find_sesssetup()` returns an in-progress session for session setup. `smbsrv_session_sesssetup_finished()` requires non-NULL `auth_session_info`, steals it onto the session, and records auth time. `smbsrv_session_new()` allocates a session, assigns a random VUID with `idr_get_new_random()`, steals optional `gensec_ctx`, links the session, installs a destructor, and records connect time.

State and persistence: all state is connection-local and talloc-scoped. The destructor removes the VUID idtree entry and list link. No disk persistence is involved.

Dependencies and integration: depends on idtree_random, talloc ownership, GENSEC authentication context, and auth session info. SMB session setup handlers use it to separate in-progress authentication from usable authenticated sessions.

Risks and test signals: VUID exhaustion fails session creation. Freeing the session on NULL auth info prevents partially authenticated sessions from surviving programmer errors. Signals come from session setup, reconnect, authentication, and multi-session smbtorture tests.
