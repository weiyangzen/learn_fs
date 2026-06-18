# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/structure.go

Purpose: defines shared structured log data models for read-cache, chunk-cache, job, and buffered-read log parsers.

Important APIs/types/functions: `CommonReadLog`, `StructuredReadLogEntry`, `ReadChunkData`, `Job`, `JobData`, `ChunkCacheReadLogEntry`, `ChunkDownloadLogEntry`, internal `handleAndChunkIndex`, `LogEntry`, `BufferedReadLogEntry`, and `BufferedReadChunkData`.

Control flow: there is no executable flow; the file supplies DTO-style structs embedded or populated by parser files. `StructuredReadLogEntry` embeds `CommonReadLog` and appends chunk details; `BufferedReadLogEntry` extends the same common read fields with fallback/restart flags.

State/persistence behavior: these structs represent in-memory parsed logs only. Timestamps are stored as seconds/nanos fields for parser comparison, while generic `LogEntry` stores a `time.Time`.

Dependencies/integration: consumed by JSON read parser, buffered read parser, job parser, and integration tests that assert read/cache behavior.

Risks/test signals: the models assume parser ordering means chunks are timestamp-sorted; if log files are not pre-sorted, downstream tests may infer incorrect chronology.
