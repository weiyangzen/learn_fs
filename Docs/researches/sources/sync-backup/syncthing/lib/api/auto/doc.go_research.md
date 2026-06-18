# sources/sync-backup/syncthing/lib/api/auto/doc.go

Purpose: Package documentation and generation directive for compiled web assets.

Important APIs/types/functions: Contains `go:generate go run ../../../script/genassets.go -o gui.files.go ../../../gui` and declares package `auto`.

Control flow: No runtime control flow.

State and persistence behavior: No runtime state. Generation creates source files from the GUI asset tree.

Dependencies and integration points: Generated `gui.files.go` supplies `Assets()` consumed by `api_statics.go` and tested by `auto_test.go`.

Risks: If the generation command or GUI path changes, the compiled asset bundle can become stale or missing.

Test signals: `auto_test.go` verifies the generated or fallback bundle at runtime.
