# Research: sources/object-store/minio-mc/cmd/ilm-rule-import.go

Purpose: implements `mc ilm rule import`, replacing bucket lifecycle configuration from JSON read on stdin.

Important APIs/types/functions: `ilmImportCmd`, `ilmImportMessage`, `readILMConfig`, `checkILMImportSyntax`, and `mainILMImport`.

Control flow: validates one target, reads a `lifecycle.Configuration` from `os.Stdin` with colorjson decoder, rejects configs with zero rules to avoid accidental lifecycle deletion, writes via `SetLifecycle`, and prints success.

State and persistence: replaces server-side bucket lifecycle configuration.

Dependencies/integration points: MinIO lifecycle client, stdin, colorjson, console message formatting.

Risks: full-replacement operation can remove existing rules not present in input. No explicit validation beyond JSON decode and non-empty rule list is performed here; server validation handles invalid lifecycle data.

Test signals: no direct tests; should cover invalid JSON, empty rules rejection, and successful SetLifecycle.
