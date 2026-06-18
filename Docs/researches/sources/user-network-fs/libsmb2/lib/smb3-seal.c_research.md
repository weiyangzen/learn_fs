# sources/user-network-fs/libsmb2/lib/smb3-seal.c

## Purpose
Implements SMB3 message encryption and decryption ("sealing") using AES-128-CCM transform headers.

## Important APIs, Types, And Functions
Exports `smb3_encrypt_pdu` and `smb3_decrypt_pdu`. It uses the SMB3 transform protocol marker `{0xFD,'S','M','B'}`, `aes128ccm_encrypt`, `aes128ccm_decrypt`, and encryption keys from `struct smb2_context`.

## Control Flow
Encryption returns immediately unless context sealing and PDU sealing are both enabled. It computes the total compound payload length, allocates a transform buffer, writes the 52-byte transform header, fills part of the nonce with `random()`, writes original message size, algorithm id, session id, copies all compound PDU outgoing iovecs after the transform header, and encrypts/signs the payload in place with AES-CCM. Decryption verifies AES-CCM over the transform header and payload, stores decrypted bytes in `smb2->enc`, resets the normal receive state to parse a fresh SMB2 header from that buffer, calls `smb2_read_from_buf`, and frees the temporary decrypted buffer.

## State And Persistence
Encryption stores `pdu->crypt`, `pdu->crypt_len`, and may clear `pdu->seal` on allocation failure. Decryption temporarily uses `smb2->enc`, `enc_len`, and `enc_pos`, resets `spl` and `recv_state`, and transfers ownership of the decrypted payload away from the input iovec.

## Dependencies And Integration Points
Integrated directly with `socket.c`: encrypted outgoing PDUs are sent as a single transform payload, and encrypted incoming frames are detected by transform header magic and then re-fed through normal parsing. It depends on negotiated encryption keys and share/session sealing decisions.

## Risks
Nonce generation uses `random()` and only fills bytes 20 through 30, so nonce quality and uniqueness should be reviewed. No explicit transform header validation beyond successful CCM authentication is visible here. Only AES-128-CCM is used. Decryption frees `smb2->enc` after parsing, so callbacks must not retain pointers into decrypted input beyond PDU lifetime.

## Test Signals
Round-trip encrypted single and compound PDUs, wrong key/tag failure, seal disabled/enabled combinations, nonce uniqueness under repeated sends, malformed transform headers, decrypted chained messages, and memory ownership after callbacks.
