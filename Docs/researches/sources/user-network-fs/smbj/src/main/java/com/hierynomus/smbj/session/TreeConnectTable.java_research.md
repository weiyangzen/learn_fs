<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java

Purpose: Per-session table of open tree connects, indexed by tree id and share name.

Important APIs/types/functions: register(Share), getOpenTreeConnects(), getTreeConnect(long), getTreeConnect(String), and closed(long) use a ReentrantReadWriteLock around two HashMaps.

Control flow: Session registers shares after successful TREE_CONNECT, uses share-name lookup for connectShare cache hits, iterates open tree connects during logoff, and removes entries when TreeDisconnected events arrive.

State and persistence behavior: In-memory mapping only. getOpenTreeConnects returns a snapshot copy so callers can close without holding locks.

Dependencies and integration points: Depends on Share and TreeConnect metadata.

Risks: Share-name lookup is exact string matching and may miss case-insensitive SMB equivalence. register overwrites silently by id or name. closed removes by id and then by the removed share's name, so inconsistent maps can leave stale entries.

Test signals: Register and lookup both keys, close event removal, snapshot semantics during concurrent close, duplicate share name/id behavior, and concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java -->
