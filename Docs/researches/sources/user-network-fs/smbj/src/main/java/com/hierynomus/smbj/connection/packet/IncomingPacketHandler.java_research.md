# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/IncomingPacketHandler.java

Purpose: `IncomingPacketHandler` defines the packet-handler chain contract.

Important APIs and control flow: handlers must implement `handle(SMBPacketData<?>)` and `setNext(IncomingPacketHandler)`.

State, dependencies, and integration: `Connection` uses the interface to compose decryption, compounding, validation, credit, async, deserialization, and dead-letter stages.

Risks: chain ordering is external to the interface and security-sensitive. Tests should verify the composed chain order rather than isolated interface behavior only.
