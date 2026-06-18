## sources/test-tools/kdevops/workflows/fstests/cifs/Kconfig

Purpose: Configures SMB/CIFS fstests execution, including whether to use a kdevops-provisioned SMB server and which SMB3 security variants to test.

Important APIs/types/functions: Public symbols include `FSTESTS_USE_KDEVOPS_SMBD`, `FSTESTS_SMB_SERVER_HOST`, `HAVE_DISTRO_CIFS_PREFERS_MANUAL`, `FSTESTS_CIFS_MANUAL_COVERAGE`, and section selectors `FSTESTS_CIFS_SECTION_SMB3`, `_SMB3_SEAL`, and `_SMB3_SIGN`.

Control flow: The file first selects server mode. Manual coverage exposes user-facing section choices. Non-manual mode hides selectors and defaults to SMB3 only, leaving encryption and signing variants off.

State and persistence: Selections are stored in `.config`; server host values and section booleans are later emitted as Make/Ansible arguments.

Dependencies and integration points: Selecting the kdevops server pulls in `KDEVOPS_SETUP_SMBD`. The parent fstests workflow sources this file only for CIFS runs, and the Makefile maps selected sections to `fstests_cifs_*` args.

Risks and test signals: External server mode has weak validation and depends on a pre-created hierarchy. Test signals are generated inventory for `smbd`, rendered `fstests_smb_server_host`, and successful mount/run of smb3, seal, or signing sections.
