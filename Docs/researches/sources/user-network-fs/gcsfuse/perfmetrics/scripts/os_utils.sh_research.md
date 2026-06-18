<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh

## Purpose
Shared shell utilities for OS detection, Go architecture mapping, and distro-aware package installation.

## Important APIs, Types, And Functions
`get_os_id`, `get_go_arch`, and `install_packages_by_os`; guarded against multiple sourcing with `_OS_UTILS_SH_LOADED`.

## Control Flow
Reads `/etc/os-release`, maps `uname -m` to Go arch strings, and dispatches package installation across apt, yum-family, and pacman systems with name remapping for Python/fuse packages.

## State And Persistence Behavior
Runs package-manager commands and may install Python CRC dependencies via pip using a repo requirements file.

## Dependencies
Requires `readlink`, distro package managers, sudo, optional `fuser`, and `OS_UTILS_DIR` path relation to tools requirements.

## Integration Points
Sourced by `install_go.sh` and suitable for other perfmetric installers.

## Risks And Edge Cases
Apt lock retry only wraps `apt-get update`, not install. RHEL `python3-crcmod` install path depends on a relative requirements file outside this subset.

## Test Signals
No tests here; behavior is covered only by scripts that source it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh -->
