# Research: sources/object-store/minio-mc/cmd/ilm-rule-edit.go

Purpose: implements `mc ilm rule edit`, modifying fields on an existing lifecycle rule.

Important APIs/types/functions: `ilmEditCmd`, `ilmEditFlags`, `ilmEditMessage`, `checkILMEditSyntax`, and `mainILMEdit`.

Control flow: requires one target and non-empty `--id`. It fetches lifecycle config, parses edit options, locates the matching rule by ID, applies non-nil option fields through `ilm.ApplyRuleFields`, writes the full config back, and prints success.

State and persistence: mutates bucket lifecycle configuration server-side.

Dependencies/integration points: shared add flags, `cmd/ilm` option parsing and field application, MinIO lifecycle API.

Risks: if no lifecycle config exists, it creates an empty config but then fails to find the rule, which is correct but indirect. Field application resets some mutually exclusive fields and can leave others unchanged by design; tests must protect this partial-update contract.

Test signals: no direct tests for edit; should cover enable/disable, date versus days reset, missing ID, and not-found rule behavior.
