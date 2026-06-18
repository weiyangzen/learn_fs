# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_sign.c

## Purpose
Implements SMB1 message signing for integrity protection using MD5 over the MAC key, SMB header with sequence number, and message body.

## Key Elements
`smb_sign_init` obtains the MD5 mechanism, copies the SMB1 session key into the VC MAC key buffer, and initializes the SMB1 signing sequence number to 2 after session setup. `smb_compute_MAC` digests the MAC key, an aligned copy of the SMB header with the signature field replaced by the sequence number and zero, and the remainder of the message chain, then returns the first 8 bytes of the MD5 digest as the SMB signature.

`smb_rq_sign` writes either the computed signature into the SMB1 header or the special fake signature value used before SPNEGO/NTLMSSP has produced a MAC key. `smb_rq_verify` recomputes the expected reply signature from `sr_rseqno`, compares it with the header signature, logs failures, and in debug builds can test nearby sequence numbers using `nsmb_signing_fudge`.

## Dependencies
Uses `nsmb_kcrypt` MD5 helpers, VC signing key state, SMB1 request/reply chains, STREAMS mblk traversal, SMB header constants, and debug/error logging helpers.

## Behavior/Risks
Signing sequence numbers must be assigned consistently in the IOD (`sr_seqno` for request and `sr_rseqno` for reply) or all replies fail verification. The code assumes the first mblk contains a contiguous SMB header. Returning success when no MAC key is present allows negotiation/authentication phases to proceed, but once signing is active a bad signature returns `EBADRPC`. Any change to header offsets or sequence handling can break interoperability with SMB1 servers.
