# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BackupTLSConfig.h

Purpose: declares backup TLS and blob credential setup configuration.

Important APIs and types: `BackupTLSConfig` stores TLS certificate, key, CA, password, verify-peers string, and blob credential file paths. `setupTLS()` returns whether TLS setup succeeded. `setupBlobCredentials()` loads blob credentials and also considers the `FDB_BLOB_CREDENTIALS` environment source after network setup.

State and persistence: state is process configuration. Credentials are read from paths/environment into network/blob-store runtime configuration, not persisted here.

Dependencies and integration: used by backup tooling and blob-store setup paths. The implementation depends on `g_network` being initialized for blob credentials.

Risks: credential ordering and environment fallback affect which credentials are available. TLS setup failure must be surfaced before backup agents attempt remote operations. Secrets in fields should not be logged casually.

Test signals: backup CLI/config tests and blob credential integration tests; no local unit tests in the header.
