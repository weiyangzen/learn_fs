## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/Credentials.h

Purpose: Defines credential providers for gRPC channels/servers, including insecure credentials and TLS/mTLS credentials with dynamic or static certificate sources.

Important APIs/types/functions: `GrpcCredentialProvider` declares `serverCredentials()`, `clientCredentials()`, and `validate()`. `GrpcInsecureCredentialProvider` returns insecure server/channel credentials. `GrpcTlsCredentialProvider` builds a `FileWatcherCertificateProvider` from `TLSConfig` key/cert/CA paths, configures server mTLS, watches roots and identity pairs, and returns TLS credentials. `GrpcTlsCredentialStaticProvider` uses in-memory key/cert/CA strings through `StaticDataCertificateProvider`, primarily for tests.

Control flow: TLS providers initialize certificate providers and options in constructors. Credential accessors build gRPC server/channel credentials from stored options. `validate()` delegates to provider credential validation.

State and persistence behavior: Dynamic TLS provider watches certificate files and reloads from the filesystem. Static provider stores credential material in memory. No repository/database persistence.

Dependencies and integration points: Enabled only under `FLOW_GRPC_ENABLED`; depends on gRPC experimental TLS APIs, Flow knobs for refresh delay, and `TLSConfig`. Used by gRPC server/client setup, including `AsyncGrpcClient`.

Risks: gRPC experimental APIs and watch behavior can change. mTLS is always required for TLS server options, so clients must present valid certificates. Static provider comments indicate watch calls are still needed even for static data, which is a subtle test/runtime dependency. Credential validation must be checked before accepting configuration.

Test signals: Insecure credentials creation, dynamic provider validation against cert files, certificate rotation, static provider validation, mTLS client rejection without certs, and refresh-delay behavior.
