# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2IsOutstandingPacketHandler.java

Purpose: `SMB2IsOutstandingPacketHandler` verifies that a response maps to a known request unless it is an oplock break notification.

Important APIs and control flow: it reads the message sequence number, checks `OutstandingRequests`, and forwards either the packet or a `DeadLetterPacketData`.

State, dependencies, and integration: placed before signature verification and processing, so unknown responses do not deserialize into promises.

Risks: dead-lettering unknown packets may leave malicious or stray data only logged. Tests should cover known request, unknown request, oplock notification, and dead-letter forwarding.
