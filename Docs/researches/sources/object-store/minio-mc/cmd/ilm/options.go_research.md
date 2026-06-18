# Research: sources/object-store/minio-mc/cmd/ilm/options.go

Purpose: converts ILM CLI options into MinIO lifecycle rules and applies partial edits to existing rules.

Important APIs/types/functions: `RemoveILMRule`, `LifecycleOptions`, `LifecycleOptions.Filter`, `LifecycleOptions.ToILMRule`, pointer helpers, `GetLifecycleOptions`, and `ApplyRuleFields`.

Control flow: `GetLifecycleOptions` reads CLI flags, supports deprecated and current flag names, infers prefix from target path when `--prefix` is absent, parses sizes with humanize, uppercases tier names, enforces transition-day requirements when tiers are set, and limits expiry action flags. `ToILMRule` builds a lifecycle rule and validates it via parse helpers. `ApplyRuleFields` applies only provided fields, resetting mutually exclusive date/day/delete-marker fields where appropriate.

State and persistence: pure in-memory transformation; callers persist with `SetLifecycle`.

Dependencies/integration points: MinIO lifecycle structs, `probe`, `xid`, `humanize`, and `cli.Context`.

Risks: edit semantics are partial and nuanced. Prefix inference from target path is deprecated but still active. Some validation is split between option parsing and `parse.go`, so changes can introduce inconsistent acceptance.

Test signals: `options_test.go` covers filter construction. More tests are needed for `GetLifecycleOptions`, `ToILMRule`, and `ApplyRuleFields`.
