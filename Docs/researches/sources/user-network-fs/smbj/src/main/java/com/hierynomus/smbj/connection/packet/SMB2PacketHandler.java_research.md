# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2PacketHandler.java

Purpose: `SMB2PacketHandler` is a typed base class for handlers that operate on `SMB2PacketData`.

Important APIs and control flow: `canHandle` checks the data type; `doHandle` casts and calls `doSMB2Handle`.

State, dependencies, and integration: superclass for async, compound, credit, outstanding, process, and signature handlers.

Risks: raw casts are safe only because `canHandle` gates the path. Tests should cover delegation for SMB2 and pass-through for non-SMB2 data.
