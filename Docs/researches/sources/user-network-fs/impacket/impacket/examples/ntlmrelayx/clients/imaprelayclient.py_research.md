# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/imaprelayclient.py

## Purpose
`imaprelayclient.py` implements IMAP and IMAPS NTLM relay target clients for mail servers such as Exchange. It drives IMAP `AUTHENTICATE NTLM` manually enough to relay NTLM type 1 and type 3 tokens.

## Important APIs, Types, and Functions
`IMAPRelayClient` provides the ntlmrelayx client interface. It stores an IMAP tag in `authTag`, sends raw IMAP lines with `imaplib`, and marks successful sessions authenticated. `IMAPSRelayClient` changes only the default port and connection class. `PROTOCOL_CLIENT_CLASSES` registers both variants.

## Control Flow
`initConnection()` connects, allocates a tag with `_new_tag()`, logs capabilities, and requires `AUTH=NTLM`. `sendNegotiate()` sends `AUTHENTICATE NTLM`, waits for the continuation prompt, sends the base64 type 1 blob, decodes the server continuation challenge, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO if present, sends the base64 type 3 blob, and waits for the tagged response to decide between `STATUS_SUCCESS` and `STATUS_ACCESS_DENIED`.

## State and Persistence Behavior
The active `imaplib` session, `authTag`, and IMAP state are the only retained state. A successful relay sets `self.session.state = 'AUTH'`. There is no local persistence.

## Dependencies and Integration Points
It depends on Python `imaplib`, Impacket NTLM/SPNEGO, and the common `ProtocolClient`. SOCKS IMAP plugins can later proxy through the authenticated IMAP session.

## Risks and Edge Cases
The code uses `imaplib` private methods and raw `send()`/`readline()` flows, so Python version or server response formatting differences can break parsing. It compares capabilities against a string literal, and failures may raise after logging instead of returning a relay status.

## Test Signals
Test IMAP and IMAPS servers that advertise or omit `AUTH=NTLM`, continuation prompt mismatch, SPNEGO-wrapped auth, tagged OK/NO/BAD responses, logout cleanup, and NOOP keepalive.
