# Research: sources/object-store/minio-mc/cmd/ilm-tier-remove.go

Purpose: implements `mc ilm tier remove`/`rm`, deleting a remote tier target.

Important APIs/types/functions: `adminTierRmFlags`, `adminTierRmCmd`, and `mainAdminTierRm`.

Control flow: validates exactly `ALIAS NAME`, rejects empty tier names, requires hidden `--dangerous` when hidden `--force` is set, creates admin client, and calls `RemoveTierV2` with `madmin.RemoveTierOpts{Force}`.

State and persistence: removes or disconnects server-side tier configuration. Force can be irreversible for a tier with data.

Dependencies/integration points: madmin tier remove API and shared `tierMessage` output.

Risks: hidden force/dangerous path is intentionally high risk. Non-force removes only empty tiers, relying on server enforcement.

Test signals: no direct tests; cover arity, force/dangerous coupling, and request option propagation.
