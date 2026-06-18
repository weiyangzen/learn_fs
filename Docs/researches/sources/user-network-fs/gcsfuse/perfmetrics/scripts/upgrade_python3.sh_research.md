<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh

## Purpose
Builds Python 3.11.9 from source under `$HOME/.local/python-3.11.9` for gcloud compatibility.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Installs build dependencies using apt or yum, downloads Python source to `/tmp`, configures with optimizations, builds with `nproc`, and runs `make altinstall`.

## State And Persistence Behavior
Mutates system packages and local user prefix, leaves source under `/tmp/Python-3.11.9` unless overwritten by later runs.

## Dependencies
Depends on apt/yum, compiler toolchain, development libraries, wget, make, and network access.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Build from source is slow, unpinned by checksum, and only handles apt/yum families.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh -->
