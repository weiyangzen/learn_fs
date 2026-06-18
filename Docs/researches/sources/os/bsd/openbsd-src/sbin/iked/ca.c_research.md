# File Research: sources/os/bsd/openbsd-src/sbin/iked/ca.c

`ca.c` implements the privileged certificate-authority subprocess for `iked`. It owns local CA/certificate stores, private/public key material received from the parent, certificate request/reply handling, AUTH signing requests, raw public-key fallback, and OpenSSL-based certificate validation.

Key paths include `caproc()`/`ca_run()` process startup, `ca_reset()`/`ca_reload()` store creation and reload, `ca_getreq()` certificate selection for outbound CERT payloads, `ca_getcert()` peer CERT validation, and `ca_getauth()` signing of AUTH payloads. The CA process communicates with parent, IKEv2, and control processes through imsg dispatchers.

Certificate handling supports X.509 certificates, bundled certificates with untrusted intermediates, local supplemental certificate chains, raw RSA/ECDSA public keys, CRLs, optional partial-chain validation, and optional OCSP validation. It computes RFC7296 CERTREQ SHA-1 subject-public-key-info digests and matches identities through ASN.1 DN or subjectAltName.

Security-relevant details: private key material lives in the CA process, certificates are validated through `X509_STORE_CTX`, CRL flags are enabled only after CRLs load, raw public-key validation maps peer IDs to files under the public-key directory, and AUTH signing falls back to `IKEV2_AUTH_NONE` on signing failure. Input bundle parsing is strict on type/length boundaries.

Notable coupling: depends heavily on `iked.h`, `ikev2.h`, OpenSSL, `config_getkey()`, `ikev2_msg_authsign()`, OCSP helpers, imsg helpers, and policy/SA identity structures.
