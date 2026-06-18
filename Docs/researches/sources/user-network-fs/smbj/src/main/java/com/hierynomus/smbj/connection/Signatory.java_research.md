# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Signatory.java

Purpose: `Signatory` abstracts packet signing and verification.

Important APIs and control flow: `sign(SMB2Packet, SecretKey)` may return a wrapped packet; `verify(SMB2PacketData, SecretKey)` returns signature validity.

State, dependencies, and integration: implemented by `PacketSignatory` and `NoSignatory`; injected into sessions and packet handlers.

Risks: callers must provide the correct dialect/session/channel signing key. Tests should verify both implementations through the shared interface and packet handler integration.
