# File Research: sources/virtualization/open-iscsi/usr/auth.c

Implements the iSCSI CHAP authentication state machine used during login/security negotiation. The file is explicitly single-threaded per `iscsi_acl` instance and uses OpenSSL EVP/RAND for digest computation and challenge generation.

Major components:
- CHAP digest support for MD5, SHA1, SHA256, and optionally SHA3-256.
- Key/value parsing and serialization for `AuthMethod`, `CHAP_A`, `CHAP_N`, `CHAP_R`, `CHAP_I`, and `CHAP_C`.
- Text conversion helpers for numbers, hex binary (`0x...`), and base64 binary (`0b...`).
- Receive and send key blocks with duplicate, too-long, and overflow tracking.
- Negotiation phases: configure, negotiate, authenticate, done, error.
- Local state handles algorithm negotiation and responses to peer challenges.
- Remote state sends challenges and verifies peer responses.
- Transit-bit handling enforces legal security phase progression.

Public API:
- `acl_init` wires caller-provided buffers into one auth context and defaults to `CHAP,None`.
- `acl_recv_begin`, `acl_recv_key_value`, `acl_recv_transit_bit`, and `acl_recv_end` drive each received login/security message.
- `acl_send_key_val` and `acl_send_transit_bit` expose generated response keys.
- Configuration functions set username, password, CHAP algorithms, mutual auth, and IPsec policy.
- `acl_chap_compute_rsp` computes a CHAP response.
- `acl_chap_auth_request` validates the target’s response using `session->username_in` and `password_in`.
- `acl_dbg_status_to_text` maps internal failure states to human-readable text.

Notable details:
- `acl_data` currently just copies password bytes; older comments still talk about decrypting.
- If mutual authentication is required but no valid response was processed, final status is forced to fail.
- The code detects reflected challenges and identical local/remote passwords in mutual CHAP paths.
- Passwords are cleared after local digest computation, but context/session password fields persist by design.
