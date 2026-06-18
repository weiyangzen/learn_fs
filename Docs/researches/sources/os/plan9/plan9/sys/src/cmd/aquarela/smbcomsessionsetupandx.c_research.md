# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomsessionsetupandx.c

Server handler for `SMB_COM_SESSION_SETUP_ANDX`.

Key behavior:
- Parses AndX command, max buffer size, max mux, vc number, session key, LM/NT password lengths, capabilities, password bytes, account/domain/native strings.
- Lowercases account name.
- Enforces one user per VC.
- Validates 24-byte LM and NT MS-CHAP responses on first setup.
- Uses Plan 9 auth challenge/response and `auth_chuid`.
- Stores client identity strings and marks session established.
- Returns native OS/LANMAN/domain strings and chains if requested.

Interactions:
- Consumes challenge created by `smbnegotiate`.
- Uses `smbresponse` wrappers and `smbchaincommand`.

Notable details:
- Supports non-extended-security MS-CHAP style authentication only.
