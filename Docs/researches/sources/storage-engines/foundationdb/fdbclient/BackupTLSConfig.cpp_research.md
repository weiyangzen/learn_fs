# sources/storage-engines/foundationdb/fdbclient/BackupTLSConfig.cpp

Purpose: This file applies backup-agent TLS and blob credential configuration before network use. It bridges command-line or environment-provided backup TLS settings into global FoundationDB network options and blob credential file discovery.

Important APIs and types: It implements `BackupTLSConfig::setupBlobCredentials` and `BackupTLSConfig::setupTLS`. The relevant fields are `blobCredentials`, `tlsCertPath`, `tlsCAPath`, `tlsKeyPath`, `tlsPassword`, and `tlsVerifyPeers`. It uses `g_network->global(INetwork::enBlobCredentialFiles)` and `setNetworkOption` with `FDBNetworkOptions`.

Control flow: `setupBlobCredentials` reads `FDB_BLOB_CREDENTIALS`, splits it on `:`, ignores empty entries, appends them to the instance list, then appends all collected credential paths to the network-global blob credential vector if present. `setupTLS` conditionally sets certificate path, CA path, TLS password, key path, and peer verification. Each option is wrapped in its own `try/catch`; failures print a clear stderr message and return `false`.

State and persistence behavior: No files are written. The durable inputs are credential/TLS files outside this code. Runtime state is process-global network configuration and the global blob credential file vector consumed by `IBlobStoreEndpoint::updateSecret`.

Dependencies and integration points: It depends on `NativeAPI.actor.h`, `flow/network.h`, `BackupTLSConfig.h`, and the blob credential loading code in `BlobStoreCommon.cpp`. It is used by backup command-line tools and agents before opening blobstore containers or TLS cluster connections.

Risks: `FDB_BLOB_CREDENTIALS` uses `:` as a separator, which is natural on Unix but awkward for Windows-style paths. TLS options must be applied before network initialization or connection use. Error reporting goes to stderr, so callers must honor the boolean return value. Blob credential global state is append-only for the process and can accumulate duplicates.

Test signals: There are no in-file tests. Useful validation is startup behavior with valid/invalid TLS paths, blobstore authentication with credentials supplied by environment and command line, and errors emitted by `BlobCredentialFile*` traces when `BlobStoreCommon` reads the configured files.
