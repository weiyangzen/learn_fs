# sources/test-tools/syzkaller/dashboard/app/api_test.go

## Purpose

`api_test.go` focuses on API authentication/authorization helpers, emergency-stop effects, crash reporting priority calculation, and upload URL generation. It provides targeted coverage for security and operational behavior around `api.go`.

## Important tests and covered functions

- `TestClientSecretOK`, `TestClientOauthOK`, `TestClientSecretFail`, and `TestClientSecretMissing` test `checkClient` for API key and OAuth-subject authentication.
- `TestClientNamespaceOK`, `TestClientMethodOK`, `TestClientMethodNotOK`, and `TestClientNamespaceAccess` validate namespace client lookup, method allowlists, and global-vs-namespace wrapper behavior.
- `TestEmergentlyStoppedEmail`, `TestEmergentlyStoppedReproEmail`, `TestEmergentlyStoppedExternalReport`, `TestEmergentlyStoppedEmailJob`, and `TestEmergentlyStoppedCrashReport` test the dashboard's emergency stop behavior across email, repro, external reporting, patch testing jobs, and crash ingestion.
- `TestUpdateReportingPriority` checks `Crash.UpdateReportingPriority` ordering based on revoked/non-revoked repros, title match, manager priority, repository priority, and architecture.
- `TestCreateUploadURL` verifies `apiCreateUploadURL` returns a configured bucket plus UUID-like upload object path.

## Control flow and state behavior

The client tests construct temporary `GlobalConfig` values and call `checkClient` directly, asserting returned namespace and error values. Namespace access tests call real client methods to ensure `nsHandler` and `globalHandler` reject clients in the wrong scope.

Emergency-stop tests create dashboard state, trigger `/admin?action=emergency_stop`, then verify no subsequent email, report, job notification, or bug creation occurs. These tests rely on datastore persistence of `EmergencyStop` and mocked time advancement to trigger scheduled or asynchronous dashboard processing.

Reporting priority tests construct synthetic crashes and call the method directly, then assert priority ordering after compaction. Upload URL tests mutate config with `transformContext` and call the global API client.

## Dependencies and integration points

This file depends on `NewCtx`, test API clients, App Engine test context, `dashapi`, target architecture constants, and testify assertions. It integrates with admin UI actions, email polling helpers, job polling/completion helpers, and the global dashboard config.

## Risks and edge cases

Security regressions in `checkClient` could allow namespace clients to call global methods, global clients to mutate namespace state, or clients to bypass method allowlists. Emergency stop is broad operational safety state; incomplete coverage in handlers could still allow work to leak after stop. Priority scoring uses large additive constants, so future changes could accidentally collapse ordering between repro class, title match, manager priority, and architecture.

## Test signals

The file gives high-signal negative tests for auth and stop behavior. It complements broader end-to-end tests by directly checking error identity (`ErrAccess`), error text for wrapper violations, and exact absence of downstream side effects after emergency stop.
