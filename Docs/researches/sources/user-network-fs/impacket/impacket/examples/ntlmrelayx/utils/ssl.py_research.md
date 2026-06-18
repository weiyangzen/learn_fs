# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/ssl.py

Purpose: provides generic SSL helpers for SOCKS plugins that need to present a local TLS server, such as IMAPS and LDAPS, plus certificate generation for those local-only sessions.

Important APIs and control flow: `generateImpacketCert()` creates a 2048-bit RSA key and five-year self-signed X.509 certificate with CN `impacket`, then writes private key and certificate into the same PEM file. `SSLServerMixin.wrapClientConnection()` creates a pyOpenSSL `SSL.Context(TLS_METHOD)`, lowers cipher restrictions with `ALL:@SECLEVEL=0`, loads the configured combined PEM, generates it if missing/invalid, creates an `SSL.Connection` around `self.socksSocket`, sets accept state, and replaces `self.socksSocket`.

State and persistence: certificate generation writes a combined key/cert file to `/tmp/impacket.crt` by default. Mixin state mutation is the socket replacement on the instance.

Dependencies and integration: depends on pyOpenSSL and `impacket.LOG`. It integrates by multiple inheritance into SOCKS relay plugins that expose `self.socksSocket`.

Risks and test signals: `/tmp/impacket.crt` is shared, predictable, and contains a private key. No SAN or hostname matching is attempted because it is intended for local use. Tests should cover cert generation, fallback when cert load fails, socket replacement with an accept-state connection, custom cert path support, and concurrent plugin startup using the same default file.
