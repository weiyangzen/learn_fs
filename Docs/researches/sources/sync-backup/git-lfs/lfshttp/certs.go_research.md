# sources/sync-backup/git-lfs/lfshttp/certs.go

Purpose: Configures TLS certificate verification, client certificates, and root CA pools from Git config and environment.

Important APIs/types/functions: `isCertVerificationDisabledForHost`, `isClientCertEnabledForHost`, `decryptPEMBlock`, `getClientCertForHost`, `getRootCAsForHostFromGitconfig`, `appendCertsFromFilesInDir`, `appendCertsFromFile`, `appendCerts`, and `appendCertsFromPEMData`.

Control flow: Host-specific `sslverify=false` or global skip disables verification. Client certs require both host `sslKey` and `sslCert`, expand paths, read PEM files, decrypt encrypted keys via credential helper when needed, and load `tls.X509KeyPair`. Root CAs are selected from `GIT_SSL_CAINFO`, URL config, `GIT_SSL_CAPATH`, or `http.sslcapath`, with schannel exceptions.

State and persistence behavior: Reads certificate/key files and may approve/reject passphrases via credential helpers. Builds in-memory `x509.CertPool`; no direct file writes.

Dependencies and integration points: Used by `Client.Transport` to configure `tls.Config`. Depends on `config.URLConfig`, `tools.ExpandPath`, Cygwin path translation, credential helper context, and tracer logging.

Risks and edge cases: Missing or unparsable cert files log and return unchanged pools. Returning nil preserves system roots; returning an empty pool would be dangerous, so append helpers avoid that. Decryption assumes helper returns a password.

Test signals: `certs_test.go` covers CA file/path config and env sources, schannel behavior, and global/host SSL verification disabling.
