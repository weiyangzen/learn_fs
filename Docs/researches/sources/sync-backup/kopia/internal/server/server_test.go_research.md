<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_test.go -->
# sources/sync-backup/kopia/internal/server/server_test.go

- Purpose: Integration-tests API-server-backed repository access, authentication, UI access restrictions, object/manifest operations, and remote notifications.
- Important APIs/types/functions: `TestServer`, `TestGRPCServer_AuthenticationError`, `TestServerUIAccessDeniedToRemoteUser`, `remoteRepositoryTest`, `remoteRepositoryNotificationTest`, `mustWriteObject`, `mustReadObject`, `mustReadManifest`, `mustListSnapshotCount`.
- Control flow: Tests start an in-process test server, connect via API server config, cancel the original context to verify detached operation, then perform repository reads/writes, manifest saves/deletes, object prefetch, notification sends, and UI/remote user access checks.
- State and persistence: Uses repotesting repositories, remote API repository clients, temporary caches, snapshot manifests, notification profile manifests, and HTTP test server counters.
- Dependencies and integration points: Integrates `apiclient`, `servertesting`, `repotesting`, `repo`, `content`, `snapshot`, `notifyprofile`, `notification`, and webhook senders.
- Risks and edge cases: Access-control expectations depend on route-specific CSRF policy; notification tests use one webhook success and one failing path but do not validate all sender types.
- Test signals: This is high-value integration coverage for server API repository behavior and remote notification forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_test.go -->
