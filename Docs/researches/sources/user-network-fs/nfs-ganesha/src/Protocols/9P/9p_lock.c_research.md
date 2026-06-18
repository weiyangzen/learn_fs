## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lock.c

Purpose: implements 9P byte-range locking over Ganesha state management.

APIs and flow: `_9p_lock` parses fid, lock type, flags, byte range, proc id, and client id. It resolves the client id through `getaddrinfo`, obtains a 9P state owner with `get_9p_owner`, handles read/write locks under grace and object state lock, verifies open mode with `status2`, calls `state_lock`, maps conflicts to `_9P_LOCK_BLOCKED`, and unlocks through `state_unlock`.

State/dependencies: uses fid embedded `state_t`, Ganesha state owner/lock tables, NFS grace tracking, and FSAL open status. The `flags` field is logged but blocking behavior is effectively nonblocking.

Risks/tests: array indexing in debug strings assumes valid lock type before switch, DNS/client-id parsing can fail, and blocking lock semantics are incomplete. Test lock type validation, grace behavior, wrong open modes, conflicts, unlock ranges, and client owner reuse.
