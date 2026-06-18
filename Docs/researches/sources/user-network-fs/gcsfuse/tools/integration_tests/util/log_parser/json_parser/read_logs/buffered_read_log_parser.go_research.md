# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser.go

## Purpose

Parses JSON-formatted gcsfuse buffered-read trace logs into structured per-file-handle entries with chunk reads, request IDs, execution times, fallback status, random seek count, and restart status.

## Important APIs, control flow, and dependencies

The parser defines regexes for `ReadFile`, buffered `ReadAt` requests, simple `ReadAt` responses, fallback messages, and restart messages. `ParseBufferedReadLogsFromLogReader` loads lines, calls `filterAndParseLogLineForBufferedRead`, and drops handles that never produced buffered chunks. Parsing functions create `BufferedReadLogEntry` on `ReadFile`, append `BufferedReadChunkData` on `ReadAt` requests, map request ID back to handle/chunk in `opReverseMap`, fill execution time on responses, and mark fallback or restart events.

## State, persistence, dependencies, and integration points

Parser state is held in maps keyed by file handle and request ID. It depends on log message ordering: a `ReadFile` must precede `ReadAt`, and a request must precede its response. Non-JSON lines are ignored, while malformed JSON logs with expected fields missing produce errors.

## Risks and test signals

Risks include brittle regexes tied to exact log strings, JSON type assertions that can panic on malformed timestamp/message shapes, and fallback logs for unknown handles being treated as errors. Signals are structured maps with expected common read fields, chunks, execution time, fallback/random seek count, restarted flag, and expected errors for missing prerequisite logs.
