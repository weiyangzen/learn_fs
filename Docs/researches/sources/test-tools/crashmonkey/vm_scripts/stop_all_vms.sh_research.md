# sources/test-tools/crashmonkey/vm_scripts/stop_all_vms.sh

Purpose: powers off all configured VirtualBox VMs.

Important APIs/types/functions: environment `num_vms`, `VBoxManage controlvm ubuntu16-vm<i> poweroff`. Control flow loops from 1 to `num_vms` and powers off each VM.

State/persistence behavior: abruptly powers off VM runtime state, similar to pulling power. Dependencies/integration: operator utility for shutting down a VM farm.

Risks/test signals: no validation or graceful ACPI shutdown, and no error handling for stopped/missing VMs.
