# sources/test-tools/kdevops/scripts/libvirt_pool.sh

## Purpose
Provides shell helpers for discovering libvirt storage pool support and mapping a base directory to a virsh pool name/path.

## Important APIs
`get_can_sudo()` probes noninteractive sudo and returns `y` or `n`. `get_pool_vars()` detects Fedora user-session behavior from `$OS_FILE`, sets `CAN_SUDO`, and chooses `REQ_SUDO`. `virsh_works()` checks sudo/session capability, `virsh` availability, and `virsh pool-list`. `virsh_get_pool_list()` fills global `POOL_LIST`. `virsh_path_in_pool_list_exists()`, `virsh_path_pool_list_name()`, and `virsh_path_pool_list_path()` search pool XML paths for `$BASE_DIR`.

## Control flow and state
The script is a library with global variables: `USES_QEMU_USER_SESSION`, `CAN_SUDO`, `REQ_SUDO`, `POOL_LIST`, `POOL_PATH`, and expected caller-provided `BASE_DIR` and `OS_FILE`. Several search helpers call `exit` after printing a match, so they are designed for script execution contexts as much as pure sourcing.

## Dependencies and integration
Uses `sudo`, `which`, `virsh`, `grep`, `sed`, and `awk`. It integrates with kdevops libvirt setup scripts that need to decide if storage pool commands should run through sudo or a user session.

## Risks and test signals
`get_can_sudo()` treats any sudo output not containing `may not` as usable sudo, including password prompts or other errors. XML is parsed with grep/sed rather than XML tooling. Test signals are `virsh_works` returning `y`, a non-empty `POOL_LIST`, and correct base directory pool lookup on Fedora and non-Fedora hosts.
