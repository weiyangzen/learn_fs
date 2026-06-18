# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CreditGrantingPacketHandler.java

Purpose: `SMB2CreditGrantingPacketHandler` returns server-granted credits to the sequence window.

Important APIs and control flow: for each SMB2 response it calls `creditsGranted(header.getCreditResponse())`, logs availability, and delegates onward.

State, dependencies, and integration: depends on the connection `SequenceWindow`; placed before async/final response processing so credits become available quickly.

Risks: blindly releases credit response values; malformed or unexpected values depend on packet parsing validation. Tests should cover zero and positive grants, waiting sender release, and handler ordering relative to promise delivery.
