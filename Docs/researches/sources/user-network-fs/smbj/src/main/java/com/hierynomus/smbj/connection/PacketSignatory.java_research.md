# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketSignatory.java

Purpose: `PacketSignatory` signs outgoing SMB2 packets and verifies incoming packet signatures.

Important APIs and control flow: `sign` wraps a packet when a secret key is available. The wrapper sets the signed flag, writes through a `SigningBuffer` that updates a MAC as bytes are emitted, then copies the first signature bytes into the SMB2 header signature position. `verify` recalculates the MAC over header bytes before the signature, an empty signature field, and the remaining message, then compares with the received signature.

State, dependencies, and integration: it uses `SecurityProvider` MACs keyed by session signing keys and is used by `Connection` and signature verification handler.

Risks: offset arithmetic is security-critical. `verify` compares byte-by-byte with early exit rather than constant time. `SigningBuffer` overrides selected write methods only. Tests should include known SMB signing vectors, signed flag/header placement, tamper detection, and null-key pass-through.
