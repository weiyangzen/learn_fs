# sources/user-network-fs/gcsfuse/tools/proxy_server/grpc_proxy.go

Purpose: transparent gRPC proxy that forwards raw protobuf bytes to a target while optionally validating incoming metadata.

Important APIs/types/functions: `rawCodec`, `validateGRPCMetadata`, and `startGRPCProxy`.

Control flow: registers a raw byte codec, creates a target client connection with insecure credentials and raw codec, installs an unknown-service handler, extracts method and metadata, validates configured headers, opens a matching target stream, then proxies messages in both directions with goroutines and returns the first directional error.

State/persistence behavior: maintains target gRPC connection and listener/server state for process lifetime. No files are written.

Dependencies/integration: started by `GRPCProxyServer.Start` in `main.go`; uses `google.golang.org/grpc` metadata/status APIs.

Risks/test signals: target connection is not explicitly closed. Metadata validation only treats non-empty expected patterns as matchable, so empty-pattern validations effectively check presence only when fail-on-missing is set.
