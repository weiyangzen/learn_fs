<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh

## Purpose
Installs top-level perfmetrics requirements, fetches Sheets credentials, and runs `populate_vm_metrics.py` for a start/end range.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It is a small operational wrapper for manual or scheduled VM metric backfill.

## State And Persistence Behavior
Installs user Python dependencies and writes credentials under `./gsheet`.

## Dependencies
Depends on pip hash requirements, gcloud storage access, and valid CLI times.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No argument validation beyond the Python script; credentials path is relative.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh -->
