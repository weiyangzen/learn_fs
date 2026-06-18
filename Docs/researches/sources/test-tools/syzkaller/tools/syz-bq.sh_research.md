<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bq.sh -->
# sources/test-tools/syzkaller/tools/syz-bq.sh

## Purpose

BigQuery coverage aggregation orchestration script.

## Important APIs, Types, and Functions

getopts for workdir/duration/date/namespace/repo/branch/client; git clone/fetch/log, GNU date, `bq query`, `go run syz-covermerger`.

## Control Flow

Updates kernel repo, picks latest commit before date, checks BigQuery partition row count for date range, then invokes syz-covermerger with dashboard upload settings.

## State and Persistence Behavior

Persists/updates repo under workdir and merger outputs/uploads.

## Dependencies and Integration Points

Requires Git, bq auth, GNU date, Go build, dashboard API.

## Risks and Edge Cases

Unquoted vars are whitespace-fragile; date/commit pipeline is format-sensitive; client name optionality is weak.

## Test Signals

Mock git/bq tests and small real namespace/date integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/syz-bq.sh -->
