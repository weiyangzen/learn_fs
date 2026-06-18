# Research: sources/object-store/minio-mc/cmd/ready-main.go

## sources/object-store/minio-mc/cmd/ready-main.go

Purpose: implements `mc ready`, polling MinIO health until the cluster is ready.

Important APIs and types: `readyCmd`, `readyFlags`, `readyMessage`, and `mainReady`.

Control flow: syntax requires a target. The handler builds an anonymous admin client, creates `madmin.HealthOpts` from `--cluster-read` and `--maintenance`, then starts an immediate timer. On each tick it calls `anonClient.Healthy`, prints a `readyMessage`, returns nil if healthy, otherwise waits five seconds and retries until context cancellation.

State and persistence: read-only remote health checks. No local persistence.

Dependencies and integration: uses `madmin.AnonymousClient.Healthy`, shared global context, JSON/human output via `printMsg`, and color formatting.

Risks and tests: command can loop indefinitely for unhealthy clusters. It prints errors but does not exit immediately on unreachable states unless context is cancelled. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ready-main.go -->
