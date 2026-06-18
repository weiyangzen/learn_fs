<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json

## Purpose
HNS listing benchmark config for bucket `list-benchmark-tests-hns`.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Same twelve one-kilobyte file-count cases as the flat config, targeted at the HNS bucket.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Used to compare HNS listing behavior with the same workload shape.

## Risks And Edge Cases
The 1M folder can be very expensive and is name-skipped by default in benchmark code.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json -->
