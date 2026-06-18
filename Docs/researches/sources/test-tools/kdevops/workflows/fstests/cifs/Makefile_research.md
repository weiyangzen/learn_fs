## sources/test-tools/kdevops/workflows/fstests/cifs/Makefile

Purpose: Emits CIFS-specific fstests workflow arguments from Kconfig.

Important APIs/types/functions: Adds `fstests_cifs_enable`, `fstests_cifs_use_kdevops_smbd`, `fstests_smb_server_host`, and `fstests_cifs_section_*` values to `FSTESTS_ARGS`.

Control flow: It starts with CIFS enabled, chooses the server host from either `CONFIG_FSTESTS_SMB_SERVER_HOST` or the kdevops host prefix plus `-smbd`, then appends section args for SMB3, encrypted SMB3, and signed SMB3.

State and persistence: No file state is written. The persistent source is `.config`; the output path is Make variables that feed Ansible extra vars.

Dependencies and integration points: Included by the parent fstests Makefile when CIFS is selected. It depends on `CONFIG_KDEVOPS_HOSTS_PREFIX` for kdevops-managed server naming.

Risks and test signals: A mismatch between server host naming and inventory breaks all CIFS sections. Verify by inspecting `extra_vars.yaml` and running a CIFS dry run or mount smoke test.
