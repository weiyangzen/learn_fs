# Research: sources/object-store/minio-mc/cmd/ilm/parse.go

Purpose: parses and validates lifecycle rule fields for ILM commands.

Important APIs/types/functions: `extractILMTags`, validation helpers for transition/expiration/current date/noncurrent rules, `validateILMRule`, `parseTransitionDate`, `parseTransitionDays`, `parseTransition`, `parseExpiryDate`, `parseExpiryDays`, and `parseExpiry`.

Control flow: tag strings split on `&` and first `=`. Validation requires at least one action, enforces single expiration/transition mode, checks dates are not in the past, ensures transition before expiration, enforces storage class presence, and validates noncurrent days/storage class. Parse helpers convert `YYYY-MM-DD` dates and integer day strings into lifecycle types.

State and persistence: pure in-memory parsing/validation.

Dependencies/integration points: `lifecycle` types and `probe` errors. Called from `LifecycleOptions.ToILMRule` and `ApplyRuleFields`.

Risks: tag parsing is permissive and allows key without value. Date validation uses local current date truncated to day, so tests involving dates can be time-sensitive. STANDARD_IA minimum transition day rule is hard-coded.

Test signals: no direct parse tests; add table tests for invalid combinations and date/day parsing.
