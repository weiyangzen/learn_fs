# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneClientCache.java

Purpose: `OzoneClientCache` owns the singleton Ozone client used by request-scoped S3 endpoint producers.

Important APIs and flow: `initialize()` sets S3 auth checking and minimum OM version configuration, disables OM group rights for the gateway client, and creates an RPC client. `createClient` chooses HA or non-HA RPC creation based on OM service ID. If gRPC TLS is enabled, `setCertificate` temporarily creates a Hadoop-RPC client with S3 auth disabled to retrieve OM service certificates and installs CA certs into `GrpcOmTransport`. `cleanup()` closes the cached client.

State, dependencies, risks, and tests: state is the cached `OzoneClient` and mutable shared `OzoneConfiguration`. It integrates with `OzoneClientProducer`, OM client protocol, TLS certificate setup, and S3 thread-local auth. Risks include mutating shared config, certificate bootstrap failure, static gRPC CA state, and using a single client across requests while relying on thread-local auth cleanup. Tests should cover initialization config, HA/non-HA selection, TLS cert bootstrap, and cleanup.
