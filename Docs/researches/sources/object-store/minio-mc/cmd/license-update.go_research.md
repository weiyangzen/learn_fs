# Research: sources/object-store/minio-mc/cmd/license-update.go

Purpose: implements `mc license update`, either saving a provided license file or renewing from SUBNET.

Important APIs/types/functions: `licenseUpdateCmd`, `licUpdateMessage`, `mainLicenseUpdate`, `performLicenseRenew`, and `performLicenseUpdate`.

Control flow: accepts alias plus optional license-file path. With a file, it reads the license and calls `validateAndSaveLic`. Without a file, it loads stored SUBNET API key, fails if not registered, posts to the license-renew endpoint with API-key auth and deployment ID, then extracts and saves returned credentials.

State and persistence: updates local license/SUBNET credentials and may call SUBNET to renew license.

Dependencies/integration points: local file IO, SUBNET HTTP helpers, alias config, deployment ID header helper.

Risks: renewal requires existing API key and remote SUBNET availability. File update trusts `validateAndSaveLic` for license validation and storage.

Test signals: no direct tests; cover arg count, file read errors, unregistered renew, successful renew credential extraction.
