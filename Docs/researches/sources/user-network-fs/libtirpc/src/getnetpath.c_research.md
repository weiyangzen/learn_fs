## sources/user-network-fs/libtirpc/src/getnetpath.c

Purpose: Implements `NETPATH` iteration APIs that select visible netconfig transports in caller-preferred order.

Important APIs and control flow: `setnetpath` allocates a session and opens `setnetconfig`. If the environment variable `NETPATH` is set, it copies it and closes the netconfig session until individual entries are needed. `getnetpath` either iterates visible netconfig entries when `NETPATH` is unset, or tokenizes the copied `NETPATH` string by colon, ignores invalid netids, and returns `getnetconfigent` results tracked in a session allocation chain. `endnetpath` closes any netconfig handle, frees the copied `NETPATH`, frees all allocated netconfig entries, and releases the session. `_get_next_token` null-terminates tokens while handling backslash escapes.

State and persistence: Per-session mutable cursor state. External persistence is the environment and `/etc/netconfig`.

Dependencies and integration: Used by generic client paths when nettype defaults to `netpath`.

Risks and test signals: `_get_next_token` uses overlapping `strcpy`, noted in comments. Tests should cover unset NETPATH, escaped delimiters/backslashes, invalid netids, cleanup chains, and nested sessions.
