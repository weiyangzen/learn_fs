# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmsrelayserver.py

Purpose: implements the HTTPS WinRM relay frontend on port 5986 by default. It mirrors the HTTP WinRM relay behavior but wraps the listening server socket in a generated self-signed TLS certificate.

Important APIs and control flow: `WinRMSRelayServer.HTTPServer` creates an RSA key/certificate with CN `localhost`, writes them to temporary files, builds an `ssl.SSLContext`, and wraps the server socket. `HTTPHandler` is structurally parallel to the HTTP version: it handles `/wsman` POSTs, `PROPFIND`, `CONNECT`, auth header parsing, local multirelay auth, real target negotiate/auth, John hash output, SOCKS enqueue or attack dispatch, and target rotation through redirects.

State and persistence: server state includes the SSL context and WPAD counters. Temporary certificate and key files are created with `delete=False` and are not cleaned up by this module. Per-connection relay state includes challenge, target, protocol client, auth user, relay mode, and negotiation count. Optional persistent hash output uses the configured output file.

Dependencies and integration: depends on Python `ssl`, pyOpenSSL `crypto`, `http.server`, Impacket NTLM/hash helpers, `TargetsProcessor`, `activeConnections`, protocol clients, and configured attacks.

Risks and test signals: temporary cert/key file leakage is possible. HTTPS differs subtly from HTTP in auth headers, and `send_error()` shares the `.find('RPC_IN')` truthiness issue. Tests should cover TLS startup, certificate generation, `/wsman` routing, auth token parsing, multirelay redirect, disableMulti terminal responses, failed auth target cycling, SOCKS enqueue, attack dispatch, hash output, and temp file lifecycle expectations.
