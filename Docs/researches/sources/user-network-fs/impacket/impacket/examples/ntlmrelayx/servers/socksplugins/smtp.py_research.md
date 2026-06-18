# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/smtp.py

Purpose: implements SMTP SOCKS relay reuse on port 25. It presents a local SMTP service to a SOCKS client, steers the client toward PLAIN/LOGIN auth to learn the username, then tunnels commands through an existing relayed SMTP session.

Important APIs and control flow: `skipAuthentication()` sends a Microsoft-style `220` banner, expects `EHLO`, mirrors upstream EHLO capabilities from `getServerEhlo()` while removing NTLM/GSSAPI/STARTTLS, adds `AUTH PLAIN` and `AUTH LOGIN`, and extracts the username from `AUTH LOGIN` or `AUTH PLAIN`. It checks `activeRelays`, rejects in-use sessions, attaches `session.sock` and `session.file`, and returns SMTP `235`. `tunnelConnection()` forwards commands/responses, locally handles `QUIT`, and has a DATA loop until CRLF-dot-CRLF.

State and persistence: no persistent storage. State consists of `packetSize`, selected `username`, selected upstream `session`, and relay socket/file handles. `activeRelays` is shared with the SOCKS server and keepalive path.

Dependencies and integration: depends on `base64`, `impacket.LOG`, and `SocksRelay`; assumes SMTP protocol clients expose `session.ehlo_resp`, `sock`, and `file`.

Risks and test signals: Python 3 byte/string assumptions are visible in socket `send()` calls and base64 split handling. DATA termination may be confused by fragmentation or binary content. Tests should cover EHLO capability rewriting, AUTH LOGIN and PLAIN extraction, relay miss/in-use paths, QUIT suppression, DATA fragmentation around the terminator, and STARTTLS omission.
