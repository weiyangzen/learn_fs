# Research: sources/object-store/minio-mc/cmd/ilm-tier-verify.go

Purpose: implements hidden `mc ilm tier verify`, shared with visible `check`, to validate remote-tier configuration/connectivity.

Important APIs/types/functions: `adminTierVerifyCmd` and `mainAdminTierVerify`.

Control flow: validates exactly alias and tier name, creates admin client, calls `VerifyTier`, and prints a tier message using the invoked command name.

State and persistence: read-only validation, though server may perform remote connectivity checks.

Dependencies/integration points: madmin `VerifyTier`; visible `check` command delegates here.

Risks: connectivity checks may be slow or depend on external remote storage availability. Empty tier names are rejected locally.

Test signals: no direct tests; cover arity, empty tier, and message op for verify/check aliases.
