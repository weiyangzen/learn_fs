# sources/test-tools/syzkaller/pkg/gcpsecret/secret.go

## Purpose
Package `gcpsecret` resolves secrets from GCP Secret Manager or environment variables for syzkaller configuration. It also exposes helpers to discover the current GCP project when running on GCE/GKE.

## Important APIs, Types, And Functions
`GcpSecret(name)` reads a Secret Manager version using a background context. `GcpSecretWithContext(ctx, name)` creates a Secret Manager client, calls `AccessSecretVersion`, closes the client, and returns payload bytes. `LatestGcpSecret(ctx, projectName, key)` formats the latest-version resource path. `ProjectName(ctx)` checks `metadata.OnGCE` and returns the metadata project ID. `Resolve(ctx, val)` returns `env:` values from `os.Getenv`, `gcp-secret:` values from Secret Manager in the current project, and unprefixed values unchanged. `init` calls `runtime.KeepAlive(GcpSecret)` for dashboard/app config usage.

## Control Flow
Resolution is prefix-based. Environment lookup is local and returns empty string without error for missing variables. GCP secret lookup first determines project name, then reads the latest secret version, wrapping errors with project/secret context.

## State And Persistence Behavior
The package does not persist local state. It reads external secret state from Secret Manager and process environment. Each secret read creates and closes a client, so there is no cached client state.

## Dependencies And Integration Points
It depends on GCP metadata and Secret Manager clients, `context`, `os`, `runtime`, and `strings`. It is intended for dashboard/app configs and any syzkaller component that accepts literal, environment-backed, or Secret Manager-backed config values.

## Risks
`Resolve` silently returns an empty string for missing environment variables. `ProjectName` fails off GCE/GKE, so `gcp-secret:` values are not portable to local environments without metadata. Creating a new Secret Manager client per call is simple but may be inefficient for many secrets.

## Test Signals
No tests for this file are included in the item. Useful tests would cover prefix parsing, env fallback, off-GCE errors, and a mocked Secret Manager access path.
