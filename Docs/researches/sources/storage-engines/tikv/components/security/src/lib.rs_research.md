## sources/storage-engines/tikv/components/security/src/lib.rs

Purpose: implements TiKV security configuration, TLS credential loading, secure grpc channel/server setup, certificate reload, and common-name authorization.

Important APIs/types/functions: `SecurityConfig`, `SecurityConfigManager`, `SecurityManager`, `ClientSuite`, `Secret`, `match_peer_names`, and private helpers `check_key_file`, `load_key`, `CnChecker`, `Fetcher`, and `check_common_name`.

Control flow: `SecurityConfig::validate` enforces all-or-none CA/cert/key paths. `SecurityManager::connect` chooses insecure or TLS channel creation. `bind` chooses insecure bind or TLS bind with a credentials fetcher and optional CN checker. `Fetcher::fetch` reloads credentials only when the cert file modification time changes. Online config dispatch updates log redaction.

State/persistence: configuration is stored in an `Arc<SecurityConfig>`. Certificate contents are loaded from files on demand; server fetcher tracks last cert modification time behind a mutex. No secret content is printed because `Secret` redacts debug output.

Dependencies/integration: used by server startup, status server, PD clients, and grpc services. Depends on `grpcio`, encryption config, online config, log redaction, and filesystem metadata.

Risks: `connect` uses empty certs on load failure and defers errors to grpc connection time; CN matching is exact despite a comment mentioning wildcard support; reload watches only cert path modification, not CA/key paths independently.

Test signals: tests validate default insecure config, invalid/incomplete/valid certificate file combinations, certificate loading, and modification timestamp detection.
