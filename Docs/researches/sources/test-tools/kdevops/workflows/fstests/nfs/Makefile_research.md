## sources/test-tools/kdevops/workflows/fstests/nfs/Makefile

Purpose: Builds NFS-specific fstests Ansible variables from Kconfig.

Important APIs/types/functions: Emits `fstests_nfs_enable`, `fstests_nfs_use_kdevops_nfsd`, `fstests_nfs_server_host`, per-section `fstests_nfs_section_*`, and optional `fstests_nfs_auth_flavor`.

Control flow: The host is either an explicit configured server or the kdevops prefix plus `-nfsd`. Each selected protocol/feature section appends a boolean arg.

State and persistence: No direct state; it maps `.config` symbols to Make variables used by the parent workflow.

Dependencies and integration points: Included by the fstests Makefile for NFS. Integrates with NFS server provisioning, Kerberos/TLS roles, and fstests config generation.

Risks and test signals: Missing export information in external-server mode can pass Make but fail at mount time. Verify with generated extra-vars and a target-side mount smoke test.
