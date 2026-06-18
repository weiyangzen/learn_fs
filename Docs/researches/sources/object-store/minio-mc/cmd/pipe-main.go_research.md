# Research: sources/object-store/minio-mc/cmd/pipe-main.go

## sources/object-store/minio-mc/cmd/pipe-main.go

Purpose: implements `mc pipe`, streaming stdin to stdout or to one object target, with metadata, tags, storage class, multipart concurrency, pipe buffer tuning, checksums, and encryption.

Important APIs and types: `defaultPartSize`, `pipeCmd`, `pipeMessage`, `pipe`, `checkPipeSyntax`, and `mainPipe`. `pipeMessage` implements shared string/JSON output.

Control flow: `mainPipe` validates exactly one CLI argument, parses encryption keys, metadata and tags, and calls `pipe`. `pipe` optionally increases stdin pipe buffer size, copies stdin to stdout if no target is supplied, otherwise builds `PutOptions`, wraps stdin in a progress bar when interactive, and streams via `putTargetStreamWithURL`. Broken pipe from stdin is treated as graceful.

State and persistence: writes to the target object or file; can alter runtime GC percent when concurrent uploads are enabled. No local config writes.

Dependencies and integration: uses platform-specific `increasePipeBufferSize`, MinIO multipart sizing, SSE lookup, metadata parsing, checksum parsing, progress bars, and target stream upload helpers.

Risks and tests: `checkPipeSyntax` currently rejects zero args, while `mainPipe` still has a no-arg stdout branch that is unreachable through normal command flow. High concurrency can use substantial memory. No direct pipe command tests are in this subset.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pipe-main.go -->
