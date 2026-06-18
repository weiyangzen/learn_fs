# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/grpc/GrpcClientConstants.java

Purpose: Defines shared gRPC context and metadata keys for client hostname and client IP address propagation.

Important APIs and types: `CLIENT_HOSTNAME_CTX_KEY`, `CLIENT_HOSTNAME_METADATA_KEY`, `CLIENT_IP_ADDRESS_CTX_KEY`, and `CLIENT_IP_ADDRESS_METADATA_KEY`. The metadata keys use `Metadata.ASCII_STRING_MARSHALLER`.

Control flow: No logic beyond constant initialization and private constructor.

State and persistence behavior: Stateless constants. Values are per gRPC context or metadata instance.

Dependencies and integration points: Used by client and server interceptors and any downstream service code reading client address context.

Risks: Key names are protocol-level strings; changing them breaks propagation. Context key identity must be shared from this class rather than recreated elsewhere.

Test signals: Header round-trip tests through both interceptors validate these constants.
