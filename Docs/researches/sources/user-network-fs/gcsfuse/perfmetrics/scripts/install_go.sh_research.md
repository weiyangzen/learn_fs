<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh

## Purpose
Installs a requested Go version under `/usr/local/go` with architecture detection from `os_utils.sh`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It maps host arch to Go arch, installs `wget`/`tar`, downloads the Linux tarball, removes any existing `/usr/local/go`, extracts the new version, and verifies `go version`.

## State And Persistence Behavior
Replaces system Go under `/usr/local/go` and exports PATH only for the current shell.

## Dependencies
Depends on `os_utils.sh`, sudo, distro package managers, wget, tar, and go.dev downloads.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No checksum verification; unsupported arch returns failure; replacing Go can affect other jobs on the host.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh -->
