# sources/sync-backup/kopia/internal/grpcapi/Makefile

Purpose: documents and automates regeneration of Go protobuf and gRPC bindings for the repository server API.

Important APIs/types/functions: `rebuild` invokes `protoc` with `--go_out`, `--go_opt=paths=source_relative`, `--go-grpc_out`, and `--go-grpc_opt=paths=source_relative` against `repository_server.proto`. `install-tools` installs protobuf and Go plugins through Homebrew.

Control flow: running `make rebuild` regenerates `repository_server.pb.go` and `repository_server_grpc.pb.go` in-place with source-relative paths. `make install-tools` is a convenience target for macOS-like Homebrew environments.

State/persistence behavior: regeneration overwrites generated Go files and must be kept in sync with the `.proto` schema and generator versions. No runtime state is involved.

Dependencies/integration: depends on `protoc`, `protoc-gen-go`, and `protoc-gen-go-grpc`. The generated files are compiled into Kopia's internal gRPC API package.

Risks/test signals: `install-tools` is platform-specific and not hermetic. Generator version drift can produce large diffs even for unchanged schema semantics.
