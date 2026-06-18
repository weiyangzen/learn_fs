# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/mssql.py

Purpose: implements MSSQL/TDS SOCKS relay reuse on port 1433. It accepts a local SQL client, fakes enough prelogin/login/NTLM flow to bind the client identity to an existing relayed MSSQL session, then forwards TDS packets.

Important APIs and control flow: `skipAuthentication()` optionally detects TDS 8.0 TLS, receives prelogin, returns `TDS_PRELOGIN` with encryption based on backend requirements, receives `TDS_LOGIN7`, parses integrated security or SQL username, maps the username into `activeRelays`, loads per-user session data, and sends the saved auth answer. `_backend_requires_tds8()`, `_get_prelogin_encryption()`, `_wrap_client_connection_for_tds8()`, and `_should_wrap_sql_batch_for_backend()` handle strict encryption and SQL batch header adaptation. `tunnelConnection()` forwards client TDS to the relayed session and returns responses.

State and persistence: stores `isSSL`, `tlsSocket`, `client_tds8`, `_recv_buffer`, selected `session`, and inherited username/session data. It generates or reuses a temporary PEM for local TLS but has no long-term application state.

Dependencies and integration: depends on `impacket.tds`, `NTLMAuthChallengeResponse`, Python `ssl`, pyOpenSSL, and `generateImpacketCert()`. It integrates with MSSQL protocol clients exposing `session`, `sendTDS()`, `recvTDS()`, `tds8`, and `_wrap_sql_batch_data()`.

Risks and test signals: packet fragmentation is central; length errors corrupt TDS streams. TLS code has both legacy `tlsSocket` paths and newer `ssl.SSLContext` wrapping. Tests should cover prelogin encryption choices, integrated and SQL auth parsing, active relay selection, fragmented send/receive, EOF handling, TDS8 TLS detection, and SQL batch wrapping.
