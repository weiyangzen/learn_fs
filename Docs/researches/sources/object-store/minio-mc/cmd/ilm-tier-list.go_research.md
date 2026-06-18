# Research: sources/object-store/minio-mc/cmd/ilm-tier-list.go

Purpose: implements `mc ilm tier list`/`ls`, displaying configured remote tier targets.

Important APIs/types/functions: `adminTierListCmd`, `checkAdminTierListSyntax`, `storageClass`, `tierListMessage`, `mainAdminTierList`, and `tierTable`.

Control flow: validates one alias, fetches tiers with `ListTiers`, prints an informational message when none exist, emits JSON when requested, or sorts tiers by name and renders a lipgloss table with endpoint, bucket, prefix, region, and storage class.

State and persistence: read-only server admin query.

Dependencies/integration points: madmin tier config types and UI table library.

Risks: JSON path preserves server order while console path sorts by name. Empty tier list is not emitted as JSON because the early return precedes `globalJSON`.

Test signals: no direct tests; should cover empty list, JSON output, sorting, and storage-class extraction per provider.
