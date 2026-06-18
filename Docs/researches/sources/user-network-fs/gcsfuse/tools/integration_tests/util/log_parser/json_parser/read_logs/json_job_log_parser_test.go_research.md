# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser_test.go

## Purpose

Unit-tests job log parsing for file-cache progress logs and sparse chunk download logs.

## Important APIs, control flow, and dependencies

`TestParseJobLogsSuccessful` defines table cases with in-memory JSON logs and expected `map[string]*Job` values. It verifies a single job entry, repeated entries for the same job plus a second job with hyphenated bucket and nested object path, and a chunk download range entry with start/end offsets and bytes added.

## State, persistence, dependencies, and integration points

The test is pure and skipped when integration-test flags are set. It validates accumulation into existing map entries and construction of `ChunkCacheDownloads` separately from regular `JobEntries`.

## Risks and test signals

Risks include exact struct equality failing when new fields are added, lack of negative tests for malformed job logs, and not checking the advertised sorted order of `GetJobLogsSortedByTimestamp`. Signals are exact expected maps for all successful parser scenarios.
