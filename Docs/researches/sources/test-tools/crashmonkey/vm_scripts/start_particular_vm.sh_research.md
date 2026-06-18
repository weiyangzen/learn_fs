# sources/test-tools/crashmonkey/vm_scripts/start_particular_vm.sh

Purpose: starts one numbered VirtualBox VM headlessly.

Important APIs/types/functions: argument `vm`, `VBoxManage startvm ubuntu16-vm"$vm" --type headless`, and timestamped echo. Control flow validates one arg, then starts the VM.

State/persistence behavior: changes VM runtime state. Dependencies/integration: called by restart scripts after force-stopping a VM.

Risks/test signals: no check for already-running or missing VM; failure is only visible through VBoxManage output/exit.
