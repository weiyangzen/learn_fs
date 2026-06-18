<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java

Purpose: Thread-safe registry mapping SMB server names to Server objects.

Important APIs/types/functions: lookup(String), registerServer(Server), and unregister(String) all take a ReentrantLock around a HashMap.

Control flow: Callers register negotiated Server instances by getServerName(), later lookup by name, and remove on unregister.

State and persistence behavior: In-memory map only; lifetime is the owning client/connection context.

Dependencies and integration points: Depends on Server and Java locking collections. Used as shared registry around SMB connection management.

Risks: Name normalization is not performed, so case, FQDN vs short name, and aliases can produce duplicate entries. registerServer overwrites silently.

Test signals: Concurrent register/lookup/unregister, overwrite behavior, missing lookup, and case/alias expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java -->
