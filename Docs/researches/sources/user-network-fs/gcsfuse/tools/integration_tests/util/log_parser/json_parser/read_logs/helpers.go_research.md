# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/helpers.go

## Purpose

Contains shared parsing helpers for read-cache and job-log JSON parsers, including integer conversion, log line loading, tokenized file-cache read parsing, and job/chunk download message parsing.

## Important APIs, control flow, and dependencies

`parseToInt64` wraps decimal parsing with contextual errors. `loadLogLines` reads an entire `io.Reader` and splits by newline. `parseReadFileLog`, `parseFileCacheRequestLog`, and `parseFileCacheResponseLog` parse older tokenized file-cache messages into `StructuredReadLogEntry` and `ReadChunkData`, maintaining an operation reverse map. `parseJobFileLog` and `parseChunkDownloadLog` use regexes to populate `Job`, `JobData`, and `ChunkDownloadLogEntry`.

## State, persistence, dependencies, and integration points

All parser state is in caller-provided maps keyed by file handle, operation ID, or job ID. The helpers assume a specific token order and punctuation from gcsfuse logs, including trailing commas and `bucket:/object` formatting.

## Risks and test signals

Risks include index panics on short token arrays, regexes that do not support unusual object characters, whole-file log loading for large logs, and silent boolean parse errors in file-cache responses. Signals are downstream parser tests that validate exact job offsets, chunk ranges, file-cache chunks, and clear errors when expected patterns are absent.
