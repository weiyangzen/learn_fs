# sources/object-store/minio-mc/cmd/admin-service-restart.go

## Purpose

`admin-service-restart.go` implements `mc admin service restart`, including dry-run support, optional post-restart readiness waiting, JSON output, and an interactive Bubble Tea status UI. It is the main restart path for MinIO clusters from `mc`.

## Important APIs, Types, and Functions

The command is declared as `adminServiceRestartCmd` with `--dry-run` and `--wait` flags. `serviceRestartUI` is a Bubble Tea model driven by a `spinner.Model` and an `atomic.Value`. `serviceRestartMessage` serializes restart result state, durations, server URL, and `madmin.ServiceActionResult`. Key functions are `checkAdminServiceRestartSyntax`, `initServiceRestartUI`, and `mainAdminServiceRestart`.

## Control Flow

The handler validates exactly one target alias, creates an admin client, starts a goroutine that calls `client.ServiceAction` with `madmin.ServiceActionRestart`, and falls back to the older `ServiceRestart` API if needed. It sends a restart message immediately, then, when `--wait` is set, creates an anonymous admin client and polls `Healthy` every 500 ms under a 2-second health timeout until the cluster reports healthy. Non-JSON mode runs a Bubble Tea UI; JSON mode drains messages until state `done`.

## State and Persistence Behavior

The file does not persist client-side state. Cluster state is changed through admin service APIs. Local runtime state is held in channels, contexts, durations, and the UI model. JSON output includes a deprecated `timeTaken` field for compatibility.

## Dependencies and Integration Points

It integrates `madmin-go` service actions, the local `newAdminClient` and `newAnonymousClient` helpers, `globalContext`, console color configuration, `printMsg`, `fatalIf`, Bubble Tea, Bubbles spinner, Lip Gloss, and color JSON encoding.

## Risks and Edge Cases

The health-wait goroutine has no max timeout and depends on the process context or user cancellation. The fallback to the legacy API intentionally hides version differences. In non-JSON mode, UI completion is driven by the `quitting` flag from `View`, so terminal rendering paths are part of command completion. Dry-run still reports restart-style messages.

## Test Signals

Useful tests would cover syntax arity, new API success, legacy fallback, dry-run option propagation, JSON sequence in wait mode, no-wait immediate completion, cancellation on UI errors, and health polling transitions from failing to healthy.
