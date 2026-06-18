# sources/sync-backup/syncthing/lib/structutil/structutil.go

Purpose: reflection helpers for applying defaults and filling nil composite fields in configuration/report structs.

Important APIs and control flow: `SetDefaults` walks a struct pointer, reads `default` tags, first offers the value or address to a `ParseDefault(string) error` implementation, then supports strings, integer types, floats, booleans, and intentionally defers `[]string` defaults. Untagged nested structs are recursed into. `FillNil` and `FillNilExceptDeprecated` allocate nil pointer chains, empty maps/slices/channels, and recurse through structs and slices of structs; deprecated fields can be skipped by name prefix. `FillNilSlices` applies comma-separated `default` tags to nil `[]string` fields only.

State and persistence: mutates caller-provided structs in memory.

Dependencies and integration: used by usage-report contract construction and configuration defaulting. Depends on `reflect`, `strconv`, and `strings`.

Risks: unsupported types and parse failures panic in `SetDefaults`. The helpers require pointers to settable structs. Reflection over unexported fields can panic when `Interface` is called if a tagged field is not interfaceable. Tests cover common defaults and nil filling.
