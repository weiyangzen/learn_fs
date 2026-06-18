# sources/test-tools/kdevops/workflows/common/Makefile

## Purpose
Maps global workflow Kconfig values into shared Ansible variables for data devices/paths, kdevops git source/version/location, make command override, and data user/group behavior.

## Important APIs, Types, and Functions
Important variables include `WORKFLOW_DATA_*`, `WORKFLOW_KDEVOPS_*`, `WORKFLOW_MAKE_CMD`, `WORKFLOW_DATA_USER`, `WORKFLOW_DATA_GROUP`, and accumulated `WORKFLOW_ARGS`. Conditional targets are `kdevops-git-reset` and `kdevops-help-menu`.

## Control Flow
The file strips Kconfig quotes and appends shared settings to `WORKFLOW_ARGS`. It emits either `infer_uid_and_group=True` or explicit `data_user`/`data_group`. Git reset/help targets exist only when kdevops git clone mode is enabled.

## State and Persistence Behavior
No direct writes; variables drive generated extra vars and target-node data partition and clone state.

## Dependencies and Integration Points
Included by the main kdevops Makefile system and integrated with `playbooks/common.yml` and global Kconfig.

## Risks and Edge Cases
Mixed quoting makes paths with spaces fragile. Incorrect data devices can lead to destructive playbook operations. `WORKFLOW_MAKE_CMD` is set here but not appended in this file.

## Test Signals
Dry-run inferred vs explicit user/group, git clone mode enabled/disabled, shell-sensitive paths, and generated extra vars.
