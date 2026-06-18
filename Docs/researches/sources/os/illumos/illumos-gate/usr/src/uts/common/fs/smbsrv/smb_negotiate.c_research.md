# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_negotiate.c

This file implements SMB1 negotiate handling, including dialect selection, SMB2 upgrade negotiation, SMB1 capability advertisement, security mode setup, and dialect-specific response encoding.

Key responsibilities:
- Maintains SMB dialect string-to-code mapping.
- Parses client dialect proposals from an SMB1 negotiate request.
- Chooses the highest supported dialect allowed by server min/max protocol configuration.
- Handles SMB2 negotiation through an SMB1 negotiate request when SMB2 dialects are selected.
- Encodes SMB1 negotiate responses for core, LanMan, NT LM 0.12, and NT LM 0.12 extended-security variants.
- Sets session receive buffer sizes for old DOS/LanMan vs NT dialect behavior.
- Updates session state from established to negotiated.

Important functions:
- `smb1_newrq_negotiate` is called directly by the reader thread for the initial SMB1 negotiate and manually decodes enough request framing to dispatch negotiation.
- `smb_pre_negotiate` parses dialect strings, filters by configured protocol min/max, and stores selected dialect/index in `sr->sr_negprot`.
- `smb_com_negotiate` validates session state, handles unsupported dialects, negotiates SMB2 when appropriate, and emits dialect-specific SMB1 responses.
- `smb_post_negotiate` clears negotiation scratch storage.
- `smb_xlate_dialect` maps dialect strings to internal constants.

Negotiation behavior:
- SMB2 dialect proposals (`SMB 2.002`, `SMB 2.???`) are recognized only if max protocol allows SMB2.
- SMB1 dialects are skipped if min protocol is above SMB1.
- `NT_LM_0_12` advertises capabilities from `smb1srv_capabilities`.
- Extended security is used only when the client requests it and the server capability includes it.
- If extended security is not used, the NetBIOS domain is encoded as Unicode into a temporary message buffer.
- After successful SMB1 negotiation, `session->newrq_func` switches to `smb1sr_newrq`.

Dependencies:
- Uses mbuf marshaling for header/request decode.
- Uses `smbsr_encode_result` for response construction.
- Uses `ksocket_setsockopt` to tune receive buffer sizes.
- Calls `smb1_negotiate_smb2` for SMB2 upgrade path.

Edge cases and protections:
- Re-negotiation after session leaves `SMB_SESSION_STATE_ESTABLISHED` is rejected.
- No supported dialect logs a note and drops the virtual circuit.
- Older dialects advertise conservative max buffer/MPX/raw values.
- SMB signing bits are set only if encrypted passwords and server signing config allow them.
