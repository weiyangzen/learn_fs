<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg

## Purpose
Kokoro presubmit configuration for PR performance tests.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Defines artifact collection regexes for failed integration logs, gcsfuse logs, and sponge logs, then points `build_file` at `pr_perf_test/build.sh`.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Integrates the label-gated build shell script into Kokoro.

## Risks And Edge Cases
Artifact strip prefix assumes Kokoro checkout layout.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg -->
