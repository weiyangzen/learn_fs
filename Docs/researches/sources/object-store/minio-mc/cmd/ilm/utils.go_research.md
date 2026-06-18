# Research: sources/object-store/minio-mc/cmd/ilm/utils.go

Purpose: extracts display fields from lifecycle rules and converts a lifecycle configuration into renderable ILM tables.

Important APIs/types/functions: `getPrefix`, `getTags`, `getExpirationDays`, `getTransitionDays`, and `ToTables`.

Control flow: prefix lookup handles deprecated top-level `Rule.Prefix`, filter prefix, then `And.Prefix`. Tag formatting handles single tag or `And.Tags` joined with `&`. Day helpers convert absolute dates to days from current time. `ToTables` walks rules and appends rows to current expiration, noncurrent expiration, current transition, and noncurrent transition tables, returning only non-empty tables.

State and persistence: pure in-memory display conversion.

Dependencies/integration points: lifecycle types and table row structs from `table.go`.

Risks: absolute-date-to-days output changes with time. `DeleteAll` expiration is not surfaced in the current table fields. Deprecated prefix support is important for old configs.

Test signals: `utils_test.go` covers tag formatting; more coverage needed for prefix precedence and table inclusion.
