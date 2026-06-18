# sources/object-store/minio-mc/cmd/head-main.go

Purpose: Implements `mc head`, printing the first N lines of local/stdin/object content with optional decompression and version/rewind support.

Important APIs/types/functions: `headFlags`, `headCmd`, `headURL`, `headOut`, `parseHeadSyntax`, and `mainHead`.

Control flow: `mainHead` parses encryption and syntax, reads stdin when no args are supplied, otherwise calls `headURL` for each target. `headURL` obtains a stream and metadata, wraps gzip/bzip2 readers based on content type, and delegates to `headOut`. `headOut` uses a buffered reader and writes line by line to pretty stdout if terminal.

State and persistence: Read-only streams; writes to stdout.

Dependencies/integration: Uses `getSourceStreamMetadataFromURL`, encryption flags, rewind parsing, terminal detection, and pretty stdout.

Risks: Compression detection relies on `Content-Type`, not file extension or content encoding. `headURL` uses `context.Background()` rather than the command/global context.

Test signals: No direct tests.
