# sources/user-network-fs/samba/source4/lib/messaging/messaging_send.c

`messaging_send.c` contains the send-side subset of source4 messaging to avoid pulling full DCERPC dependencies into auth logging paths. `irpc_servers_byname()` looks up registered server IDs in `server_id_db`. `imessaging_send()` constructs a fixed message header with `message_hdr_put()`, appends an optional payload iovec, and sends through `messaging_dgm_send()`. `imessaging_send_ptr()` wraps a pointer-sized payload for in-process style messages.

The main control flow rejects non-local cluster nodes with success because source4 has no cluster transport here, normalizes pid zero to the current pid, and retries under `root_privileges()` on `EACCES`. Persistence is indirect: sends depend on the receiver's socket path and name database, but this file itself only transmits datagrams.

Risks include silent success for non-local cluster destinations, pointer payloads being meaningful only inside compatible local process layouts, and privilege retry broadening the effective send capability. Payload ownership remains with the caller until send completes. Tests should cover local sends with and without payloads, name lookups, permission fallback, and failures from stale server IDs.
