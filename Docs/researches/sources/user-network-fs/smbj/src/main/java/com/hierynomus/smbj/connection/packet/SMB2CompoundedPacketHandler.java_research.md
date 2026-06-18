# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CompoundedPacketHandler.java

Purpose: `SMB2CompoundedPacketHandler` splits compounded SMB2 responses into individual packet data views.

Important APIs and control flow: it handles only SMB2 data with `isCompounded()`, sends the current packet to the next handler, advances with `packetData.next()`, and repeats until no packet remains.

State, dependencies, and integration: placed early in the packet chain after decryption so each response is independently validated and delivered.

Risks: malformed compound offsets become `TransportException`. Compound session ID validation for decrypted packets is left elsewhere as TODO. Tests should cover two-plus response chains, final response handling, and malformed next-command data.
