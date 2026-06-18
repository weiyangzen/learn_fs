<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/extract_workflows.sh -->
# sources/test-tools/syzkaller/tools/extract_workflows.sh

## Purpose

Extracts completed dashboard AI workflow job JSON files for jobs at/after a commit date or matching a commit.

## Important APIs, Types, and Functions

Args URL/commit/output; git log timestamp, curl with optional `ACCESS_TOKEN`, jq, GNU date, mkdir/file writes.

## Control Flow

Fetches job list with `json=1`, filters finished jobs, compares created timestamp to commit date or exact revision, fetches details, writes `<output>/<workflow>/<id>.json`.

## State and Persistence Behavior

Persists downloaded JSON files in output tree.

## Dependencies and Integration Points

Requires jq, curl, Git history, GNU date, dashboard schema/network/auth.

## Risks and Edge Cases

Workflow names become dirs unsanitized; shell parsing is schema-sensitive; downloaded JSON is not validated.

## Test Signals

Local fixture server with old/new/unfinished/exact-revision jobs and auth header checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/extract_workflows.sh -->
