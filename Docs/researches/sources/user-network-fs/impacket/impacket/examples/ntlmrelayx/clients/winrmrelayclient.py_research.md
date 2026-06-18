# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/winrmrelayclient.py

## Purpose
`winrmrelayclient.py` implements a WinRM-over-HTTPS relay target client named `WINRMS`. It sends SOAP POST requests to `/wsman` and relays NTLM through HTTP authorization headers.

## Important APIs, Types, and Functions
`WinRMSRelayClient` implements connection setup, `sendNegotiate()`, `sendAuth()`, `killConnection()`, placeholder `isAdmin()`, and SOAP `keepAlive()`. It parses and can modify NTLM negotiate/auth flags for remove-MIC behavior.

## Control Flow
`initConnection()` opens `HTTPSConnection` and defaults the path to `/wsman`. `sendNegotiate()` parses the incoming type 1 token, optionally removes SIGN and ALWAYS_SIGN, probes with a SOAP POST, selects NTLM or Negotiate from `WWW-Authenticate`, sends base64 type 1 auth, and parses the returned challenge. `sendAuth()` unwraps SPNEGO, logs NTLMv2/channel-binding risk heuristics, sends base64 type 3 auth, and treats any non-401 response as success. `keepAlive()` sends a shell-create SOAP envelope.

## State and Persistence Behavior
The client stores `path`, HTTPS connection, `authenticationMethod`, `negotiateMessage`, `lastresult`, and constant XML payloads. It does not write files.

## Dependencies and Integration Points
It uses `HTTPSConnection`, `ssl`, regex header parsing, Impacket NTLM/SPNEGO, ntlmrelayx config flags, and WinRM SOAP conventions. It mirrors HTTP relay behavior but with POST/SOAP semantics.

## Risks and Edge Cases
The negotiate path computes a modified `self.negotiateMessage` but base64 encodes the original `negotiateMessage` variable, so remove-MIC behavior may be ineffective. Success uses non-401 status only. `isAdmin()` is a stub, and the keepalive SOAP target is hard-coded to `windows-host:5986`.

## Test Signals
Test `/wsman` default path, NTLM and Negotiate header parsing, connection failures, remove-MIC behavior, NTLMv2 logging, 401 denial, non-401 success, response caching, and keepalive SOAP handling.
