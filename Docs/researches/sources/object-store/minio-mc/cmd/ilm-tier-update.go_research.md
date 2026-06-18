# Research: sources/object-store/minio-mc/cmd/ilm-tier-update.go

Purpose: exposes visible `mc ilm tier update` as the credential update command.

Important APIs/types/functions: `ilmTierUpdateCmd`, reusing `adminTierEditFlags` and `mainAdminTierEdit`.

Control flow: command metadata and help only; runtime logic is fully shared with hidden `edit`.

State and persistence: mutates server-side tier credentials via shared handler.

Dependencies/integration points: depends on `ilm-tier-edit.go`.

Risks: changes to edit flags/handler immediately affect update. Help should remain aligned with the shared implementation.

Test signals: command registration test should verify update is visible and delegates to edit handler.
