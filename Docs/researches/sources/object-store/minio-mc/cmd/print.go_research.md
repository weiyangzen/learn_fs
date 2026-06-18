# Research: sources/object-store/minio-mc/cmd/print.go

## sources/object-store/minio-mc/cmd/print.go

Purpose: centralizes command message printing for human-readable and JSON output modes.

Important APIs and types: `message` requires `JSON() string` and `String() string`; `printMsg` chooses the representation based on `globalJSON`.

Control flow: for normal output it calls `String`. For JSON mode it calls `JSON`; if `globalJSONLine` is true and the JSON contains newlines, it attempts `json.Compact` to emit one line. It trims one trailing newline and writes through `console.Println`.

State and persistence: no persistent storage. Reads global output mode flags.

Dependencies and integration: every command message type in this subset implements this interface. It uses the standard JSON package only to compact output already produced by message implementations.

Risks and tests: if a `JSON` method returns invalid JSON, compaction failure is ignored and multiline output remains. It strips only suffix newline, not other whitespace. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/print.go -->
