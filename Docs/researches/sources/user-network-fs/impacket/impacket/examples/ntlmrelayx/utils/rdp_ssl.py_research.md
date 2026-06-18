# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/rdp_ssl.py

Purpose: supplies TLS helpers for the RDP relay server: loading a server TLS context from PEM files and generating temporary self-signed certificate/key pairs.

Important APIs and control flow: `ServerTLSContext.__init__()` stores private key and certificate paths. `getContext()` creates a pyOpenSSL `SSL.Context`, sets RDP compatibility and protocol-disable options, loads certificate and private key from disk, and installs them into the context. `generate_self_signed_cert()` creates a 2048-bit RSA key, a self-signed X.509 certificate with configurable CN, one-year validity, SHA256 signature, writes cert and key to `NamedTemporaryFile(delete=False)` paths, and returns `(key_file.name, cert_file.name)`.

State and persistence: `ServerTLSContext` stores file names. `generate_self_signed_cert()` persists temporary certificate and key files and leaves cleanup to callers.

Dependencies and integration: depends on pyOpenSSL `SSL`/`crypto`, `random`, and `tempfile`. It is intended for RDP relay code that needs a pyOpenSSL server context compatible with RDP TLS negotiation.

Risks and test signals: temporary file leakage is possible. `SSLv23_METHOD` is a compatibility method with security controlled by options. Tests should verify generated files exist and load, CN assignment, context options, certificate/key matching, and caller cleanup policy.
