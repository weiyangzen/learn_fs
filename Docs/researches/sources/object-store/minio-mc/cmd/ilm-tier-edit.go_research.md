# Research: sources/object-store/minio-mc/cmd/ilm-tier-edit.go

Purpose: implements hidden `mc ilm tier edit` and shared handler for visible `update`, updating remote-tier credentials.

Important APIs/types/functions: `adminTierEditFlags`, `adminTierEditCmd`, `checkAdminTierEditSyntax`, and `mainAdminTierEdit`.

Control flow: validates `ALIAS NAME`, collects credential flags into `madmin.TierCreds`, chooses one credential mode, reads GCS credential file if supplied, calls `EditTier`, and prints a tier message.

State and persistence: mutates server-side remote-tier credential configuration. Reads local credential file for GCS update.

Dependencies/integration points: `ilm-tier-update.go` reuses this handler and flag set. Uses madmin `EditTier`.

Risks: Azure service-principal branch accepts partial SP fields and relies on server validation. Static S3 credentials require both access and secret keys; `use-aws-role` overrides other modes.

Test signals: no direct tests; should cover each credential branch, insufficient credentials, and update alias wiring.
