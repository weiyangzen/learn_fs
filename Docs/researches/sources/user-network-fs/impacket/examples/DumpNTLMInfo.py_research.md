# sources/user-network-fs/impacket/examples/DumpNTLMInfo.py

## Purpose

`DumpNTLMInfo.py` extracts unauthenticated or null-auth NTLM negotiation information from SMB or RPC endpoints. It reports SMB dialect, signing requirements, read/write sizes, server time/uptime when available, NTLM target info AV pairs, OS version, and whether null session authentication succeeds.

## Important APIs, Types, and Functions

`RPC` connects to EPM on TCP 135, builds an MSRPC bind with NTLM Type 1 authentication, and parses `NTLMAuthChallenge` from the bind ack. `SMB1` and `SMB3` are lightweight custom SMB negotiation/session-setup implementations that expose `GetNegotiateResponse`, `GetChallange`, and `Authenticate`. `SmbConnection` chooses SMB1 or SMB2/3 using a wildcard negotiate and can probe SMBv1 support. `DumpNtlm` dispatches protocol-specific display paths and formats dialect, signing, I/O sizes, times, AV pairs, and null session results.

## Control Flow

The CLI selects SMB by default unless port 135 is used, in which case RPC is selected unless overridden. SMB mode opens a NetBIOS TCP session, sends a wildcard negotiate containing SMB1 and SMB2 dialects, wraps the response in `SMB1` or `SMB3`, displays negotiate metadata, sends an NTLM/SPNEGO session setup to obtain the challenge, parses AV pairs, and attempts an empty Type 3 authentication to check null sessions. RPC mode sends an authenticated bind to the endpoint mapper and parses the NTLM challenge from the bind response.

## State and Persistence Behavior

State is per-connection: sequence windows, SMB UID/session ID, cached negotiate responses, NTLM tokens, and RPC max fragment size. No credentials are stored and no files are written. Network connections are opened but explicit close behavior is minimal and mostly left to session objects/process exit.

## Dependencies and Integration Points

The script depends on Impacket SMB1, SMB2/3 structs, NetBIOS session transport, SPNEGO, NTLM, DCERPC transport/RPCRT/EPM helpers, and low-level NT status constants. It integrates directly with SMB ports 139/445 and RPC endpoint mapper port 135.

## Risks and Edge Cases

Several method and variable names are misspelled (`Challange`, `MaxTrasmitionSize`) but internally consistent. The custom protocol code is sensitive to Impacket structure changes and SMB dialect quirks. It uses broad `except` blocks around authentication and AV pair decoding, which can hide protocol parsing failures. `DisplayDialect` duplicates the SMB 3.0.2 branch. Null session probing may be logged or blocked by modern systems. RPC and SMB connections are not always explicitly disconnected.

## Test Signals

Strong tests require mocked SMB/RPC responses or controlled Windows/Samba fixtures. Signals should include SMB1-only, SMB2/3, signing-required, signing-enabled-not-required, no SMBv1, null-session success/failure, RPC NTLM challenge parsing, AV pair decoding, and time conversion from FILETIME.
