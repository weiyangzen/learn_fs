
# sources/sync-backup/restic/internal/restic/id_int_test.go

Purpose: tests special string formatting for null and nil IDs.

`TestIDMethods` checks that a zero-value `ID` renders as `"[null]"` through pointer-aware `Str`, and that a nil `*ID` renders as `"[nil]"`. These are diagnostic strings, not canonical backend names.

State is local value data. Integration points are logging, error messages, and lock string formatting where IDs may be absent. Risks covered include panics on nil receiver and ambiguous display of null IDs.
