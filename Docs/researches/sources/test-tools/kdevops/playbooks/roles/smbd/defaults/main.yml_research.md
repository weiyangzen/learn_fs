<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml

Purpose: sets the default SMB share label used by the Samba server role and share templates.

Important APIs/types/functions: variables/facts `smbd_share_label`.

Control flow: Default variable is consumed by SMB configuration templates and add-share role.

State and persistence behavior: No direct state.

Dependencies and integration points: Integrated with `smbd/tasks/main.yml` and `smbd_add_share`.

Risks: Changing the label changes share naming expected by clients.

Test signals: Signal is rendered smb.conf with the expected share label.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml -->
