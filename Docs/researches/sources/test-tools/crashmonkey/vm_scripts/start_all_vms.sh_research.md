# sources/test-tools/crashmonkey/vm_scripts/start_all_vms.sh

Purpose: starts all configured local VirtualBox VMs headlessly, spacing startups by 15 seconds.

Important APIs/types/functions: environment `num_vms`, loop `seq 1 $num_vms`, `VBoxManage startvm ubuntu16-vm<i> --type headless`, and `sleep 15`.

Control flow: loops VM numbers, starts each, prints sleep message, and sleeps. State/persistence behavior: transitions VMs to running state.

Dependencies/integration: used by setup and restart workflows. Risks/test signals: no validation that `num_vms` is set, no check if a VM is already running, and no failure handling.
