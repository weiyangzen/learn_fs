# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbnegotiate.c

Server handler for SMB dialect negotiation.

Key behavior:
- Accepts only initial negotiation state.
- Parses dialect strings and selects `NT LM 0.12` if present.
- Returns user-security encrypted-mode negotiation response, max mux/vc/buffer/raw, session key, capabilities, current NT time, timezone, 8-byte auth challenge, and primary domain.
- Creates Plan 9 MS-CHAP server challenge state.
- Moves session state to `SmbSessionNeedSetup`.

Interactions:
- Consumed by `smbcomsessionsetupandx.c` for authentication.

Notable details:
- Sets `CAP_NT_SMBS` and optionally `CAP_UNICODE`.
- If no dialect matches, returns index `0xffff`.
