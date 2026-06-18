# Research: sources/object-store/minio-mc/cmd/ilm-tier-info.go

Purpose: implements `mc ilm tier info`, showing usage statistics for configured tiers.

Important APIs/types/functions: `adminTierInfoCmd`, `checkAdminTierInfoSyntax`, `tierInfos`, `tierInfoType`, `mainAdminTierInfo`, and `tierInfoMessage`.

Control flow: validates alias and optional tier name, disallowing a tier name with JSON output. It fetches `TierStats`, builds JSON status if requested, otherwise filters table rows by tier. If a named tier has no stats, it calls `ListTiers` to verify the tier exists and shows an empty stats row.

State and persistence: read-only server admin queries.

Dependencies/integration points: madmin `TierStats` and `ListTiers`, lipgloss table renderer, humanized bytes.

Risks: if `TierStats` fails, non-JSON path still proceeds to use `tInfos`, which can hide errors or print empty data; JSON path reports the error. Named tier matching is exact and case-sensitive.

Test signals: no direct tests; cover error path, empty tiers, named tier with no stats, and JSON restriction.
