# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2SignatureVerificationPacketHandler.java

Purpose: `SMB2SignatureVerificationPacketHandler` enforces inbound SMB2 signature expectations.

Important APIs and control flow: it skips all-ones message IDs and decrypted packets. Signed packets with nonzero session IDs and non-session-setup commands are verified using the session signing key. Missing sessions or invalid signatures are dead-lettered. Unsigned packets are allowed for interim async and oplock notifications, but dead-lettered when the session requires signing.

State, dependencies, and integration: uses `SessionTable` and `Signatory`; runs after outstanding check and before credit/async/process stages.

Risks: the explicit deviation skipping session setup signatures is protocol-sensitive. Dead-lettered required-signing packets may leave promises unresolved. Tests should cover signed valid/invalid packets, missing session, decrypted bypass, unsigned required-signing rejection, and exceptions around session setup responses.
