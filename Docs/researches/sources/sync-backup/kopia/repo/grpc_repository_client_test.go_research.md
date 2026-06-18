# sources/sync-backup/kopia/repo/grpc_repository_client_test.go

Purpose: verifies that the exported gRPC message-size limit is large enough for the largest possible splitter segment plus protocol overhead.

Important APIs/types/functions: `TestMaxGRPCMessageSize`, `repo.MaxGRPCMessageSize`, `splitter.SupportedAlgorithms`, and each splitter factory's `MaxSegmentSize`.

Control flow: iterate all supported splitters, record the maximum segment size, and fail if it exceeds `MaxGRPCMessageSize - maxGRPCMessageOverhead`.

State/persistence behavior: no repository state is created. The test protects a cross-package constant contract between object splitting and gRPC transport sizing.

Dependencies/integration: integrates the public `repo` package with the splitter registry, so newly registered splitters automatically participate.

Risks/test signals: catches oversized future splitters before they can produce contents that cannot be sent over the remote API. It does not measure real protobuf overhead or streaming behavior.
