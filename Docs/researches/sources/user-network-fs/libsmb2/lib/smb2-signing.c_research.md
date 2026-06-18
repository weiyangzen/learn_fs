# sources/user-network-fs/libsmb2/lib/smb2-signing.c

## Purpose
Calculates and adds SMB2/SMB3 PDU signatures using HMAC-SHA256 for SMB2.1 and AES-CMAC-128 for newer dialects.

## Important APIs, Types, And Functions
Public functions are `smb2_calc_signature`, `smb2_pdu_add_signature`, and stub `smb2_pdu_check_signature`. Internal AES-CMAC helpers are `aes_cmac_shift_left`, `aes_cmac_xor`, `aes_cmac_sub_keys`, and `smb3_aes_cmac_128`.

## Control Flow
`smb2_calc_signature` clears the SMB2 header signature field, then either concatenates all iovecs and runs AES-CMAC for SMB3 dialects or streams iovecs through HMAC-SHA256 for SMB2.1. `smb2_pdu_add_signature` skips most session-setup PDUs until the first successful server-to-client setup response, validates vector layout and session key presence, sets `SMB2_FLAGS_SIGNED`, recalculates the signature, and copies it into both the PDU header and serialized header iovec.

## State And Persistence
Uses `smb2->signing_key`, `session_id`, `session_key_size`, and dialect state. It mutates outgoing PDU flags and signature bytes. It temporarily allocates a contiguous message buffer for AES-CMAC.

## Dependencies And Integration Points
Called by the PDU send path before transmission and by socket receive verification logic through `smb2_calc_signature`. Depends on embedded AES and SHA/HMAC helpers and SMB2 header/iovec layout.

## Risks
`smb2_pdu_check_signature` is a stub; inbound checking is implemented elsewhere in `socket.c`, so direct users of the declared check function get no validation. AES-CMAC concatenates all iovecs into one allocation, which can be expensive for large compounded writes. The source defines `EBC` instead of likely `ECB`, though included AES code may not depend on it.

## Test Signals
Use known AES-CMAC and HMAC-SHA256 vectors, signed session setup boundary cases, unsigned session id zero PDUs, missing session keys, multi-iovec compound messages, large write signing memory behavior, and negative tests for altered signatures on receive.
