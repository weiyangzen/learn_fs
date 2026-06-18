# sources/sync-backup/kopia/internal/grpcapi/repository_server.pb.go

Purpose: generated Go protobuf bindings for `repository_server.proto`, defining message structs, enum types, oneof wrappers, getters, reflection descriptors, and raw descriptor metadata.

Important APIs/types/functions: `NotificationEventArgType`, `ErrorResponse_Code`, message structs such as `ContentInfo`, `ManifestEntryMetadata`, `RepositoryParameters`, request/response types, `SessionRequest`, `SessionResponse`, oneof wrapper structs, `File_repository_server_proto`, `file_repository_server_proto_rawDescGZIP`, and `file_repository_server_proto_init`.

Control flow: generated getters return zero values for nil receivers. `Reset`, `String`, `ProtoMessage`, and `ProtoReflect` methods satisfy protobuf runtime contracts. `init` builds descriptors, registers oneof wrapper sets for session request/response, and releases temporary go type/dependency slices.

State/persistence behavior: the file encodes the wire contract for repository sessions. Persistent compatibility is tied to field numbers, enum numeric values, map encodings, and oneof tags from the proto schema.

Dependencies/integration: depends on `google.golang.org/protobuf` reflection/runtime packages. It is consumed by Kopia gRPC clients and servers along with `repository_server_grpc.pb.go`.

Risks/test signals: this file should not be hand-edited; semantic changes belong in the proto. The main risks are schema incompatibility, generator/runtime version mismatch, or stale generated output after editing `repository_server.proto`.
