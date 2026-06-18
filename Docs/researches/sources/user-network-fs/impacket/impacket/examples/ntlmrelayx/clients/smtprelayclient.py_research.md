# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/smtprelayclient.py

## Purpose
`smtprelayclient.py` implements an SMTP NTLM relay target client for mail servers. It drives the `AUTH NTLM` command sequence using Python `smtplib`.

## Important APIs, Types, and Functions
`SMTPRelayClient` provides `initConnection()`, `sendNegotiate()`, `sendAuth()`, `killConnection()`, and `keepAlive()`. `PROTOCOL_CLIENT_CLASSES` registers the SMTP client.

## Control Flow
`initConnection()` opens an SMTP connection, sends EHLO, and verifies the EHLO response advertises `AUTH NTLM`. `sendNegotiate()` sends `AUTH NTLM`, expects reply code 334, sends the base64 type 1 token, decodes the returned challenge, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO if needed, sends base64 type 3 data, and treats SMTP 235 as success.

## State and Persistence Behavior
Only the `smtplib.SMTP` session is retained. A successful relay sets `self.session.state = 'AUTH'`. No output files or external persistence are touched.

## Dependencies and Integration Points
It depends on Python `smtplib`, `base64`, Impacket NTLM/SPNEGO, and `ProtocolClient`. Authenticated sessions can be consumed by SMTP attack or SOCKS layers if configured elsewhere.

## Risks and Edge Cases
EHLO response handling assumes string containment for `AUTH NTLM`, which may vary by Python version and server formatting. The code logs `''.join(data)` on failure even though `data` may be bytes, and STARTTLS is not handled here.

## Test Signals
Cover servers with and without `AUTH NTLM`, 334 prompt failure, challenge decoding, SPNEGO auth unwrap, 235 success, non-235 denial, SMTP close, and NOOP keepalive.
