# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_update_hostname.sh

Purpose: runs the remote hostname-update script on every local NAT-forwarded VM, passing the VM number.

Important APIs/types/functions: environment `num_vms`, fixed `remote_script=vm_remote_update_hostname_script.sh`, `sshpass rsh`, `StrictHostKeyChecking no`, password piped to `sudo`, and ports from 3022.

Control flow: loops VM numbers, invokes the remote script with the current VM number, and increments port. State/persistence behavior: changes `/etc/hostname`, `/etc/hosts`, and runtime hostname inside each VM.

Dependencies/integration: called by `setup.sh` after cloning VMs. Risks/test signals: hard-coded password, no success checks, and hostname replacement assumes old name `ubuntu16-vm1`.
