# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB1PacketHandler.java

Purpose: `SMB1PacketHandler` rejects incoming SMB1 packet data.

Important APIs and control flow: `canHandle` checks `SMB1PacketData`; `doHandle` throws `SMB1NotSupportedException`.

State, dependencies, and integration: located near the end of the connection packet chain to fail SMB1 packets after SMB2-specific handlers decline them.

Risks: multiprotocol negotiation can send SMB1 negotiate, but normal received SMB1 packets are unsupported. Tests should verify SMB1 data raises the expected transport-level failure.
