# sources/test-tools/kdevops/playbooks/smbd.yml

Purpose: wrapper playbook to set up a Samba server with shared volume and system integration.

Important APIs/types/functions: targets host group `smbd` and invokes role `smbd`.

Control flow: selects Samba hosts then delegates to the role.

State/persistence behavior: delegated to Samba role, likely packages, services, shares, and storage.

Dependencies/integration: depends on `smbd` inventory group and role availability.

Risks/test signals: wrong inventory targeting can configure unintended hosts. Test signals are Samba service and share availability.
