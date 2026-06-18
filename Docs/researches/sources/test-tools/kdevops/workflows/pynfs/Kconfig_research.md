# sources/test-tools/kdevops/workflows/pynfs/Kconfig

## Purpose
Defines Kconfig options for the kdevops pynfs workflow when `KDEVOPS_WORKFLOW_ENABLE_PYNFS` is enabled. The symbols control where pynfs source is cloned from, what revision is checked out, and whether pNFS block-layout tests are added.

## Important APIs, Types, and Functions
The important symbols are `HAVE_MIRROR_PYNFS`, `PYNFS_REPO_CUSTOM`, `PYNFS_REPO_URL`, `PYNFS_GIT`, `PYNFS_GIT_TAG`, and `PYNFS_PNFS_BLOCK`. `HAVE_MIRROR_PYNFS` is an internal boolean that depends on `USE_LIBVIRT_MIRROR` and shells out to `scripts/check_mirror_present.sh /mirror/pynfs.git`. `PYNFS_GIT` is the derived repository URL used by the Make/Ansible layer; it defaults to `DEFAULT_PYNFS_GIT_URL`, a custom URL, or a guestfs mirror URL built by `scripts/append-makefile-vars.sh`.

## Control Flow
All options are scoped inside `if KDEVOPS_WORKFLOW_ENABLE_PYNFS`. If the user does not select `PYNFS_REPO_CUSTOM` and no mirror is available, `PYNFS_GIT` uses `DEFAULT_PYNFS_GIT_URL`. If `PYNFS_REPO_CUSTOM` is selected, `PYNFS_REPO_URL` becomes visible and feeds `PYNFS_GIT`. If a libvirt mirror is available and `GUESTFS` is enabled, `PYNFS_GIT` is rewritten to the guestfs bridge mirror URL. `PYNFS_GIT_TAG` defaults to `master`; `PYNFS_PNFS_BLOCK` is an independent optional boolean.

## State and Persistence Behavior
The file contributes symbols to kdevops generated configuration, which later appears as `CONFIG_PYNFS_GIT`, `CONFIG_PYNFS_GIT_TAG`, and `CONFIG_PYNFS_PNFS_BLOCK` for Make and as extra-vars for Ansible. It does not persist runtime test results itself. The shell-backed mirror default is evaluated during configuration generation and depends on the host/mirror state at that time.

## Dependencies and Integration Points
Depends on global kdevops symbols such as `KDEVOPS_WORKFLOW_ENABLE_PYNFS`, `USE_LIBVIRT_MIRROR`, `GUESTFS`, `DEFAULT_PYNFS_GIT_URL`, and `KDEVOPS_DEFAULT_BRIDGE_IP_GUESTFS`. Integrates with `workflows/pynfs/Makefile`, which strips quotes from the generated config and passes `pynfs_git`, `pynfs_git_tag`, and optionally `pynfs_pnfs_block` into `WORKFLOW_ARGS`.

## Risks
If neither `DEFAULT_PYNFS_GIT_URL` nor a selected custom URL is valid, `PYNFS_GIT` can be empty or unusable downstream. The mirror default only applies in the `HAVE_MIRROR_PYNFS && GUESTFS` case, so mirror behavior changes with virtualization mode. `PYNFS_REPO_URL` has no default or validation beyond Kconfig typing. The pNFS block option only controls argument emission; the actual test availability depends on the pynfs checkout and server environment.

## Test Signals
Configuration tests should evaluate default, custom repo, mirror-present, and pNFS-block combinations and assert the generated `CONFIG_PYNFS_*` values. A dry-run Make test can then confirm that `workflows/pynfs/Makefile` emits the expected Ansible extra vars.
