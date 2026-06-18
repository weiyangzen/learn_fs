# sources/test-tools/crashmonkey/vm_scripts/restart_unresponsive_vms.sh

Purpose: probes each local NAT-forwarded VM with a simple `rsh echo` and restarts VMs that do not respond.

Important APIs/types/functions: environment `num_vms`, `timeout -s KILL 10 rsh`, `force_stop_vm.sh`, `start_particular_vm.sh`, ports starting at 3022, and sleeps.

Control flow: loops VM indices, executes remote `echo abc`, if output is empty force-stops and restarts the VM, otherwise prints healthy. State/persistence behavior: can abruptly restart VMs; otherwise read-only.

Dependencies/integration: maintenance utility for the VirtualBox farm. Risks/test signals: empty output can reflect transient rsh failure rather than VM hang; no graceful shutdown or retry before kill.
