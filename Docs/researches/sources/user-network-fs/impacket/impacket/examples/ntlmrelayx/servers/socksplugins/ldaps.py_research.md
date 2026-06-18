# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldaps.py

Purpose: provides the LDAPS SOCKS plugin, exposing LDAP relay reuse over a TLS-wrapped client-side SOCKS connection. It inherits LDAP behavior and registers scheme `LDAPS` on port 636.

Important APIs and control flow: `skipAuthentication()` wraps `self.socksSocket` through `SSLServerMixin.wrapClientConnection()`, then delegates to `LDAPSocksRelay.skipAuthentication()` for LDAP NTLM bind spoofing. On failure it shuts down the TLS socket; on `SSL.SysCallError` it logs and rejects the SOCKS connection. `wait_for_data()` first checks pyOpenSSL pending buffers on both sockets before falling back to `select.select()`.

State and persistence: no disk persistence. It inherits LDAP in-memory state: username, selected relay session, and `activeRelays` in-use flags. TLS state is embedded in pyOpenSSL connection objects replacing the plain socket.

Dependencies and integration: depends on `select`, pyOpenSSL, `SSLServerMixin`, and `LDAPSocksRelay`. It integrates with `socksserver.py` through plugin metadata and with LDAPS protocol clients that have relayed authenticated LDAP sockets.

Risks and test signals: `wait_for_data()` assumes both socket objects expose `pending()`, and TLS error handling is narrow. Tests should verify TLS wrapping, LDAP parent bind behavior, pending-buffer forwarding, StartTLS blocking through LDAPS, and cleanup of `inUse` when the tunnel exits or TLS closes.
