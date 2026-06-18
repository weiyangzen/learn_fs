# Research: sources/object-store/minio-mc/cmd/license-info.go

Purpose: implements `mc license info`, displaying SUBNET license or AGPL status for a cluster alias.

Important APIs/types/functions: `licenseInfoCmd`, `licInfoMessage`, `licInfo`, color helper functions, `getLicInfoStr`, `getAGPLMessage`, `initLicInfoColors`, `mainLicenseInfo`, `getLicInfoMsg`, and `licErrMsg`.

Control flow: validates one alias, initializes SUBNET connectivity in check mode, reads stored API key/license with `getSubnetCreds`, parses license if present, reports registered-without-license if only API key exists, or displays AGPL message if unregistered. Console output uses a styled table for license fields.

State and persistence: read-only local SUBNET credential/license config and possible connectivity initialization.

Dependencies/integration points: SUBNET helpers, license parser, bubbles/lipgloss table UI, colorjson.

Risks: `getLicInfoStr` assumes `IssuedAt` and `ExpiresAt` pointers are non-nil. Invalid stored license returns an error message instead of falling back.

Test signals: no direct tests; cover no creds, API key only, valid license, invalid license, and JSON output.
