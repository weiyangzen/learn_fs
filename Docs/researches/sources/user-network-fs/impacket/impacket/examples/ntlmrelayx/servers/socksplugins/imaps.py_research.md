# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/imaps.py

Purpose: implements the TLS-wrapped IMAPS variant of the IMAP SOCKS plugin. It reuses `IMAPSocksRelay` logic but exposes `PLUGIN_CLASS = "IMAPSSocksRelay"`, scheme `IMAPS`, and port 993.

Important APIs and control flow: `IMAPSSocksRelay` inherits `SSLServerMixin` before `IMAPSocksRelay`, so `skipAuthentication()` first wraps the local client-side SOCKS socket in TLS using `wrapClientConnection()`, then calls the parent IMAP authentication bypass. If the parent fails, the TLS socket is shut down. On success it changes `relaySocket` to `session.sslobj`, matching the upstream SSL IMAP session object.

State and persistence: it inherits IMAP state (`idleState`, `shouldClose`, session tag tracking, username, relay sockets) and adds no persistent storage. The TLS wrapper replaces `self.socksSocket`, so all later reads and writes operate on a pyOpenSSL `SSL.Connection`.

Dependencies and integration: integrates with `SSLServerMixin`, pyOpenSSL `SSL`, and the base IMAP plugin. It depends on active relay sessions exposing both `file` and `sslobj`.

Risks and test signals: the tunnel loop catches only `SSL.ZeroReturnError`; other TLS exceptions propagate to the SOCKS handler. It duplicates IMAP cleanup logic, so base changes can diverge. Tests should exercise TLS handshake, failed parent authentication shutdown, use of `session.sslobj`, IDLE/CLOSE cleanup under TLS, and client close behavior.
