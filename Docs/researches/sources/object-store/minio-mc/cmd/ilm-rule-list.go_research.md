# Research: sources/object-store/minio-mc/cmd/ilm-rule-list.go

Purpose: implements `mc ilm rule list`/`ls`, displaying lifecycle rules in JSON or human tables.

Important APIs/types/functions: `ilmListFlags`, `ilmLsCmd`, `ilmListMessage`, `validateILMListFlagSet`, `checkILMListSyntax`, and `mainILMList`.

Control flow: validates one target and mutually exclusive `--expiry`/`--transition`. It fetches lifecycle config, errors on no rules, applies `ilm.LsFilter`, then either prints JSON or converts config to ILM tables and renders with `go-pretty`.

State and persistence: read-only server operation.

Dependencies/integration points: `cmd/ilm` table conversion and filters, MinIO client lifecycle API, console table libraries.

Risks: filtering mutates the fetched slice in place, which is harmless locally but important if reused later. Empty filtered tables print nothing in console mode, which may be ambiguous.

Test signals: no direct tests; helper package has filter tests. CLI tests should cover flag conflict, empty config, JSON, and table rendering.
