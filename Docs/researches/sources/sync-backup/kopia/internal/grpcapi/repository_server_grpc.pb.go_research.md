# sources/sync-backup/kopia/internal/grpcapi/repository_server_grpc.pb.go

Purpose: generated gRPC-Go bindings for the `KopiaRepository` service declared in `repository_server.proto`.

Important APIs/types/functions: `KopiaRepositoryClient`, `NewKopiaRepositoryClient`, `KopiaRepositoryClient.Session`, `KopiaRepositoryServer`, `UnimplementedKopiaRepositoryServer`, `UnsafeKopiaRepositoryServer`, `RegisterKopiaRepositoryServer`, `_KopiaRepository_Session_Handler`, `KopiaRepository_ServiceDesc`, and stream aliases for client/server session streams.

Control flow: client `Session` calls `NewStream` with the service stream descriptor and wraps it in a generic bidirectional client stream. Server registration checks that `UnimplementedKopiaRepositoryServer` is embedded by value when detectable, then registers a single bidirectional stream handler that delegates to `srv.Session`.

State/persistence behavior: no persistent state, but service and method names are part of the RPC contract: `/kopia_repository.KopiaRepository/Session`.

Dependencies/integration: depends on `google.golang.org/grpc`, status/codes, and generated message types. Requires gRPC-Go v1.64.0 or later via compile-time assertion.

Risks/test signals: generated code should not be manually edited. Server implementations must embed `UnimplementedKopiaRepositoryServer` for forward compatibility unless they deliberately opt into unsafe behavior.
