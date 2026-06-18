# sources/object-store/minio-mc/cmd/admin-prometheus.go

## Purpose
Defines the `mc admin prometheus` command group for metrics configuration generation and metrics printing.

## Important APIs, types, and functions
`adminPrometheusSubcommands` registers generate and metrics. `adminPrometheusCmd` defines the group. `mainAdminPrometheus` calls `commandNotFound` for invalid invocations.

## Control flow
The group routes recognized subcommands. Bare or unknown invocations use the common not-found/help path.

## State and persistence behavior
This file has no state behavior. Subcommands read local alias config and remote metrics as needed.

## Dependencies and integration points
It integrates with the top-level admin command, global flags, and the generate/metrics command files.

## Risks and edge cases
New Prometheus subcommands require updating this registry. The group help is sparse, so subcommand help carries most user guidance.

## Test signals
Tests should verify generate and metrics are reachable and that invalid subcommands route through `commandNotFound`.
