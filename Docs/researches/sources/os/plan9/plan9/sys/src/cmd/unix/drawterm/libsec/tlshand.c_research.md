# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/tlshand.c

Implements TLS 1.0 / SSL3 handshake orchestration for drawterm over Plan 9's `#a/tls` record-layer device. Public entry points `tlsServer` and `tlsClient` create a TLS channel, bind an existing fd to it, open the hand/data files, run the handshake, then return the data fd.

Major pieces:
- `TlsConnection`, `Msg`, `TlsSec`, `Bytes`, and `Ints` model handshake state, variable-length vectors, selected algorithms, randoms, transcript hashes, and security material.
- `tlsServer2` handles server handshake: receives ClientHello, chooses cipher/compressor, sends ServerHello/Certificate/ServerHelloDone, receives RSA ClientKeyExchange, installs record secrets, verifies Finished, sends Finished.
- `tlsClient2` sends ClientHello, receives server messages, extracts certificate, performs RSA key exchange, installs secrets, and validates server Finished.
- `msgSend`, `msgRecv`, `tlsReadN`, `msgClear`, and `msgPrint` encode/decode handshake records, including compatibility handling for SSL2-format ClientHello.
- Cipher negotiation is restricted to enabled kernel TLS algorithms from `#a/tls/encalgs` and `#a/tls/hashalgs`; built-in suites are RC4-MD5, RC4-SHA1, and 3DES-SHA1.
- Security code implements TLS PRF, SSL3 PRF, Finished verification, master-secret/key expansion, PKCS#1 RSA encryption/decryption, and factotum-backed server private-key use.

Important dependencies:
- `#a/tls` control/hand/data files provide the record protocol and symmetric crypto.
- `X509toRSApub` extracts RSA public keys from certificates.
- `/mnt/factotum/rpc` signs/decrypts with the server private key.
- `md5`, `sha1`, HMAC helpers, `rsaencrypt`, and mpint routines come from Plan 9 libsec/libmp.

Notable behavior and risks:
- No client certificate support is implemented; server-side `TLSconn.cert` is cleared after handshake.
- Only RSA key exchange is supported; DHE suites are enumerated but not implemented.
- TLS version support is SSL3 and TLS 1.0 only.
- `serverMasterSecret` deliberately continues with random premaster data on RSA padding/version failure to reduce oracle behavior.
- `tlsConnectionFree` assumes a non-nil connection and clears/frees it; callers only pass allocated connections in normal paths.
