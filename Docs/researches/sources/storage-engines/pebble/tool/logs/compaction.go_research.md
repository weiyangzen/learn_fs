## sources/storage-engines/pebble/tool/logs/compaction.go

Purpose: implements `logs compactions`, a Cockroach/Pebble log parser that extracts flush, compaction, ingest, blob rewrite, and read-amplification events and summarizes them in fixed time windows.

Important APIs/types/functions: regex globals parse log context, sentinel operation kind, compaction starts/ends, flushes, ingests, read amp lines, and blob rewrites. `compactionType` mirrors Pebble compaction kinds. `compactionStart`, `compactionEnd`, `event`, `compaction`, `ingest`, `readAmp`, and `logContext` model parsed data. `logEventCollector` stores current context, open jobs keyed by node/store/job, completed events, read amps, and parse errors. Parser functions include `parseLog`, `parseLogContext`, `parseCompaction`, `parseFlush`, `parseIngest`, `parseRemainingIngestLogLine`, `parseReadAmp`, `parseBlobRewrite`, `unHumanize`, and `sumInputBytes`. `aggregator.aggregate` groups events; `windowSummary.String` renders ASCII tables for flush/ingest, compaction types and bytes, read amp average, and long-running events.

Control flow: `parseLog` scans lines, saves context when present, uses the sentinel regex to dispatch compaction/flush/ingest parsing, otherwise tries blob rewrite then read amp. Starts are stored until matching end lines arrive; missing starts are reported to stderr. `runCompactionLogs` parses all files, reads `--window` and `--long-running-limit`, aggregates, prints summaries to stdout, then prints accumulated parse errors to stderr.

State and persistence: no persistent state is written. In-memory collector state depends on log order and current context; events without context inherit the last parsed context.

Dependencies and integration: uses Pebble `manifest.NumLevels`, ASCII table helpers, Cobra flags from `logs/tool.go`, and `pebble.AllCompactionKindStrings` in tests to stay synchronized with engine compaction kinds.

Risks: parser correctness depends on evolving log text and regexes. `windowSummary.String` computes read amp average without guarding empty `readAmps`, yielding NaN if no read-amp events are in a window. Long-running sort comment says descending but comparator sorts ascending. Missing start events are printed immediately to `os.Stderr` rather than accumulated. Multi-line or reformatted logs can silently stop matching.

Test signals: regex tests cover current and 23.1 formats, unknown node/store, multilevel compactions, flushable ingests, and byte parsing. Datadriven tests validate aggregation. Sync test fails when Pebble compaction kinds are added without parser support.
