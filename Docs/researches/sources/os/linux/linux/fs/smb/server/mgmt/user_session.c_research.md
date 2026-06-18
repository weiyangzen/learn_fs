# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_session.c

This file manages SMB2 session lifetime, lookup, multichannel bindings, preauth sessions, RPC handles, and procfs session reporting.

Main behavior:
- Maintains global session IDs with `session_ida`, a `sessions_table` hash, and per-connection session xarrays.
- Optional procfs output reports sessions, clients, users, state, capabilities, signing/encryption algorithm, channel count, and tree connects.
- Session creation initializes file tables, xarrays, locks, sequence number, refcount, SMB2 flag, session ID, hash insertion, proc entry, and counters.
- Session destruction logs off tree connects, destroys file table, frees user, launches durable-handle scavenger, clears RPC handles, frees channels/preauth hash, releases IDs, and frees the session.
- Lookup APIs support per-connection lookup, global slowpath lookup, and multichannel binding validation.
- `destroy_previous_session()` handles reconnect semantics: validates same user/passkey, marks related connections for reconnect, waits idle, destroys previous file table, expires the session, and restores setup state.
- Preauth session helpers store and look up per-session preauth hash values for SMB 3.1.1 binding.
- RPC helpers map named pipes such as `srvsvc`, `wkssvc`, `samr`, `lsarpc`, and `LANMAN` to IPC RPC methods and track per-session RPC handles.

This is the main session ownership layer tying together users, channels, tree connects, file tables, durable cleanup, and IPC-backed RPC.
