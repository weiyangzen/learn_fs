# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_session.c

Read status: complete.

## Purpose
Manages ksmbd SMB2 sessions, channel binding, per-session tree connections, RPC handles, proc reporting, preauth sessions, and session teardown.

## Main Responsibilities
- Allocate/register SMB2 sessions with global hash table and per-connection xarray entries.
- Maintain session refcounts, expiration, lookup, deregistration, and destruction.
- Track channels for SMB3 multichannel/binding via session channel xarray.
- Display sessions and per-session details through proc when enabled.
- Manage per-session RPC pipe handles and map pipe names to userspace RPC methods.
- Log off tree connections, destroy open-file tables, free users, close RPC handles, free channels, release IDs, and launch durable scavenger on session destroy.
- Allocate and look up preauth session snapshots for SMB 3.1.1 channel binding.
- Destroy previous sessions when the same user reconnects with a previous session ID.

## Dependencies And Role
Central session lifecycle layer used by SMB2 session setup, tree connect, file table, RPC over IPC, multichannel, and connection teardown.

## Risks
High-risk areas are nested locking across global sessions, per-connection sessions, channels, and tree connections; session refcount ownership; previous-session reconnect waiting; and binding lookups that cross connection boundaries.
