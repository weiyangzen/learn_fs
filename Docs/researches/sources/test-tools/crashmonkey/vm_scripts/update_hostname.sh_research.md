# sources/test-tools/crashmonkey/vm_scripts/update_hostname.sh

Purpose: local/remote script to set a cloned VM's hostname to `ubuntu16-vm<N>`.

Important APIs/types/functions: one argument `num`, writes `/etc/hostname`, `sed -i` replacement in `/etc/hosts`, and `sudo hostname`. Control flow validates one arg and applies the changes.

State/persistence behavior: mutates system hostname files and runtime hostname. Dependencies/integration: copied or invoked by hostname update workflows.

Risks/test signals: assumes old hostname appears as `ubuntu16-vm1`, requires root for `/etc` writes, and can replace unintended text in `/etc/hosts`.
