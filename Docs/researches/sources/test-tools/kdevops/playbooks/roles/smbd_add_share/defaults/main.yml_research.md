<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml

Purpose: sets default ownership and mode for newly created SMB share directories.

Important APIs/types/functions: variables/facts `share_user`, `share_group`, `share_mode`.

Control flow: Defaults feed the permission task in `smbd_add_share/tasks/main.yml`.

State and persistence behavior: No direct state; controls filesystem metadata when task runs.

Dependencies and integration points: Used by SMB share addition workflows.

Risks: Mode `u=rwx,g=rwx,o=rwxt` is broad and sticky; intended semantics should be verified for multi-user tests.

Test signals: Signal is created share directory with expected owner/group/mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml -->
