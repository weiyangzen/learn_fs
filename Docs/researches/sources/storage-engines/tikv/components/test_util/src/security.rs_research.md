# Research: sources/storage-engines/tikv/components/test_util/src/security.rs

## sources/storage-engines/tikv/components/test_util/src/security.rs

Purpose: loads static TLS fixture files and builds TiKV `SecurityConfig` and grpcio channel credentials for tests.

Important APIs are `new_security_cfg`, `new_channel_cred`, and private `load_certs`. `new_security_cfg` points CA, cert, and key paths at `data/ca.pem`, `data/server.pem`, and `data/key.pem` under `CARGO_MANIFEST_DIR`, sets optional allowed CNs, default encryption config, empty override target, and redaction on. `new_channel_cred` loads cert strings and builds `ChannelCredentials` with root cert and client cert/key.

Control flow is straightforward file path construction and file reads. State/persistence are the checked-in/generated cert files under `data`; returned configs are immutable values consumed by test servers/clients.

Dependencies include `security::SecurityConfig`, `grpcio::ChannelCredentialsBuilder`, `encryption_export::EncryptionConfig`, `collections::HashSet`, and `log_wrappers` redaction options. Risks include panics if cert files are missing, static cert expiration or SAN mismatch, and tests unintentionally depending on redaction behavior. Test signals are successful secure channel creation and security tests honoring allowed CN sets.
