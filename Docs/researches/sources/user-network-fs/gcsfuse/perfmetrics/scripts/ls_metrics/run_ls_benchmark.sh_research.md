<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh

## Purpose
Sets protobuf runtime compatibility, installs FUSE/pip and hashed requirements, then runs `listing_benchmark.py` for a supplied config with `ls -R`, 30 samples, upload flags, and spreadsheet id.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It bridges periodic jobs to listing benchmarks for flat or HNS configs depending on the passed config file and GCSFuse flags.

## State And Persistence Behavior
Installs packages in user environment and sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` for the process.

## Dependencies
Requires sudo apt, pip hashes, `listing_benchmark.py`, and caller-provided `GCSFUSE_FLAGS`, upload flags, sheet id, and config file.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Argument order is positional and unvalidated; wrapper assumes `requirements.txt` exists and that user-site packages are importable.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh -->
