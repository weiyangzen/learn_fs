# sources/sync-backup/kopia/repo/grpc_repository_client_unit_test.go

Purpose: unit tests `baseURLToURI`, the helper that translates configured Kopia server URLs into gRPC dial targets.

Important APIs/types/functions: `TestBaseURLToURI`, `baseURLToURI`, and `require.ErrorContains`/`require.Equal`.

Control flow: table cases cover IPv4, IPv6, Unix socket HTTPS, `kopia://`, invalid Unix HTTP, and malformed addresses. Valid cases assert the exact dial target; invalid cases assert the expected error fragment.

State/persistence behavior: no persistent state; it validates parsing and scheme policy.

Dependencies/integration: protects integration between local config `APIServerInfo.BaseURL` and `grpc.NewClient` target syntax, including Unix socket support.

Risks/test signals: catches regressions in accepted schemes or host/port formatting. It does not validate TLS behavior or actual dialing.
