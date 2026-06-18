<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java

Purpose: Mutable model of negotiated server identity and capabilities for a remote SMB server.

Important APIs/types/functions: Constructor records serverName and port. init(UUID, SMB2Dialect, int, Set<SMB2GlobalCapability>) one-time initializes negotiated identity. Getters expose serverGUID, dialectRevision, securityMode, and capabilities. validate(Server other) compares another server against this initialized identity.

Control flow: Created before negotiation, initialized once after negotiation, then used as a consistency record. validate returns true only when GUID, dialect, security mode, and capabilities match.

State and persistence behavior: In-memory fields only. initialized prevents duplicate init but getters do not guard against uninitialized access.

Dependencies and integration points: Depends on SMB2Dialect and SMB2GlobalCapability. Stored by ServerList and likely connection/session setup code.

Risks: validate assumes other fields are non-null; comparing uninitialized servers can throw NullPointerException. capabilities set is stored by reference and can be externally mutated if caller passes a mutable set.

Test signals: One-time init enforcement, validation success/failure per field, uninitialized behavior, and mutation of capability set after init.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java -->
