# Research: sources/object-store/minio-mc/cmd/ilm-tier-check.go

Purpose: registers visible `mc ilm tier check` as a remote-tier connectivity validation command.

Important APIs/types/functions: `ilmTierCheckCmd`, which delegates to `mainAdminTierVerify`.

Control flow: this file only declares command metadata and help. Runtime validation and server call are shared with the verify implementation.

State and persistence: read-only validation through server admin API.

Dependencies/integration points: uses `mainAdminTierVerify` from `ilm-tier-verify.go`.

Risks: shares output operation name with `ctx.Command.Name`, so messages distinguish `check` from hidden `verify`.

Test signals: command wiring test should verify `check` is visible and calls the verify handler.
