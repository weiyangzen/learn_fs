# sources/sync-backup/kopia/tests/end_to_end_test/api_server_repository_test.go

## Purpose
End-to-end API server repository tests for htpasswd/repository-user auth, transparent client reconnect after server restart, remote snapshot writes, JSON log upload, and GRPC manifest pagination.

## Important APIs, Types, and Functions
`TestAPIServerRepository_htpasswd`, `TestAPIServerRepository_RepositoryUsers`, `testAPIServerRepository`, `verifyServerJSONLogs`, `verifyFindManifestCount`, and `TestFindManifestsPaginationOverGRPC`. Uses `apiclient`, `serverapi`, `servertesting.ConnectAndOpenAPIServer`, `repo.Repository`, `repo.WriteSession`, and CLI server commands.

## Control Flow
The shared helper creates snapshots as multiple users, starts a TLS server with either htpasswd or repository users, opens a remote repo client, creates a write session, shuts the server down, restarts it on the same address/cert, validates read reconnection and broken write-stream behavior, connects a CLI client, creates remote snapshots, verifies server-side blob growth and snapshot counts, shuts down, verifies logs, and checks dead-server connection returns quickly. The GRPC test writes 10,000 large-label manifests and ensures paginated `FindManifests` returns all unique labels.

## State and Persistence Behavior
Creates repositories, user files or repository users, TLS cert/key files, server logs, manifests, blobs, and remote write sessions. Server restarts intentionally break existing streams while preserving repository state.

## Dependencies and Integration Points
Covers CLI server lifecycle, API/GRPC clients, auth, TLS fingerprints, repository remote protocol, manifest listing pagination, blob storage, snapshot upload, log upload, and control shutdown.

## Risks
Timing-sensitive startup/shutdown, large manifest volume, and dependency on reconnect behavior. The dead-server connection call is not checked for returned error in the source, only elapsed time, so it mainly guards retry duration.

## Test Signals
Signals include successful reconnect for read operations, failed stale write session after restart, correct snapshot visibility as `foo@bar`, remote writes producing server blobs, JSON logs containing client/server spans, quick failure to dead server, and complete GRPC pagination over large responses.
