# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2AsyncResponsePacketHandler.java

Purpose: `SMB2AsyncResponsePacketHandler` handles interim SMB2 asynchronous responses.

Important APIs and control flow: it retrieves the matching request, logs round-trip time, and if the packet is an intermediate async response, stores the server async ID and stops processing. Final async responses continue down the chain.

State, dependencies, and integration: depends on `OutstandingRequests`; request async ID is later used by cancel packets.

Risks: assumes the request exists after earlier outstanding check. It does not extend expiration timers. Tests should cover pending async response, final async response, cancel ID use, and missing request behavior.
