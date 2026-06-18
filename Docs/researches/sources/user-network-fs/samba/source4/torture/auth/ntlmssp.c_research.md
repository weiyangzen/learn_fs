# sources/user-network-fs/samba/source4/torture/auth/ntlmssp.c

## Purpose
This torture test validates NTLMSSP signing behavior through Samba’s GENSEC NTLMSSP implementation. It checks deterministic signatures for known session keys and negotiation flags and verifies expected failure modes for wrong endpoint direction, missing session keys, and shortened signatures.

## Important APIs, Types, And Functions
The main test is `torture_ntlmssp_self_check`; `torture_ntlmssp` registers it as `"NTLMSSP self check"`. The test uses `gensec_client_start`, `gensec_set_credentials`, `gensec_want_feature`, `gensec_start_mech_by_oid`, `gensec_ntlmssp_sign_packet`, `gensec_ntlmssp_check_packet`, and `ntlmssp_sign_init`. It inspects `struct gensec_ntlmssp_context` and `struct ntlmssp_state`.

## Control Flow
The test starts a client GENSEC context with command-line credentials, requests sign and seal, selects NTLMSSP, injects a known session key and flags, initializes signing, signs a fixed data blob, and compares with an expected signature. It then asserts that checking the just-generated packet fails because it is the wrong end and that clearing the session key produces `NT_STATUS_NO_USER_SESSION_KEY`. A second context repeats the test with a shorter key and different flags, comparing the non-sequence portion of the signature and checking truncated signature failure.

## State And Persistence
State is confined to talloc-owned GENSEC contexts and injected NTLMSSP state. No external files or server state are modified.

## Dependencies And Integration Points
The file integrates torture assertions, command-line credentials, loadparm GENSEC settings, NTLMSSP private state, and auth/gensec signing code. It is part of the auth torture suite.

## Risks And Test Signals
Risks include dependence on internal NTLMSSP structs, fixed expected bytes changing if signing algorithms or sequence handling changes, and use of command-line credentials even though the test mostly injects keys. Passing this test signals stable NTLMSSP signature generation, correct error mapping for missing keys and direction mismatch, and robust handling of short signatures.
