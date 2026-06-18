## sources/storage-engines/pebble/tool/logs/compaction_test.go

Purpose: tests regex extraction, context parsing, aggregation output, byte parsing, and compaction-kind synchronization for `logs compactions`.

Important APIs/types/functions: constants define representative 23.1 and current log lines for compactions, multilevel compactions, flushes, read amp, unknown node/store, and flushable ingestion. `TestCompactionLogs_Regex` checks specific capture groups for sentinel, compaction, flush, read amp, and ingest regexes. `TestParseLogContext` verifies timestamp/node/store extraction including tenant prefixes and `?` IDs. `TestCompactionLogs` runs datadriven files under `logs/testdata`, writing `log` inputs to temp files, parsing into a collector, and summarizing with configurable window/long-running duration. `TestParseInputBytes` covers old and new humanized byte formats. `TestCompactionKindToolSupport` compares supported parser kinds against `pebble.AllCompactionKindStrings`.

Control flow: regex tests iterate table cases and assert matches are non-nil and exact. Datadriven tests maintain collector state until a `reset` command, allowing multi-file sequences. The sync test excludes flush-logged kinds and maps `blob-file-rewrite` to the parser’s `blob-rewrite` spelling.

State and persistence: temp log files are written for datadriven parsing only. Collector state is intentionally reusable within a datadriven test to simulate multi-log input.

Dependencies and integration: depends on `datadriven`, `pebble.AllCompactionKindStrings`, and parser internals from `compaction.go`. It directly guards compatibility with upstream log format and compaction kind additions.

Risks: tests assert selected regex groups but not every capture. Datadriven coverage is only as broad as files under `logs/testdata`. Sync test detects missing kind names but not semantic aggregation errors for a new kind.

Test signals: high-value drift detector for log format changes, old/new byte-unit formats, node/store context changes, flushable ingest parsing, and enum synchronization.
