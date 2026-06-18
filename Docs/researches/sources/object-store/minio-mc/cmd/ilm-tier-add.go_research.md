# Research: sources/object-store/minio-mc/cmd/ilm-tier-add.go

Purpose: implements `mc ilm tier add`, configuring a remote tier target for MinIO ILM transition.

Important APIs/types/functions: `adminTierAddFlags`, `adminTierAddCmd`, `checkAdminTierAddSyntax`, `supportedAWSTierSC`, `fetchTierConfig`, `tierMessage`, `tierMessage.SetTierConfig`, and `mainAdminTierAdd`.

Control flow: validates `TYPE ALIAS NAME`, converts type with `madmin.NewTierType`, builds a provider-specific `madmin.TierConfig` from flags, creates an admin client, and calls `AddTier` or hidden `AddTierIgnoreInUse` when `--force` is used. Provider branches support MinIO, S3, Azure, and GCS credentials/options.

State and persistence: persists remote-tier configuration on the MinIO server. Reads GCS credential files locally.

Dependencies/integration points: madmin tier constructors, server admin APIs, console/colorjson output.

Risks: credential validation is complex, especially S3 role modes and Azure service principal fields. Tier names are uppercased before creation. Hidden force bypasses in-use checks and needs careful guard coverage.

Test signals: no direct tests; provider matrix validation and error cases should be unit tested with fake CLI contexts.
