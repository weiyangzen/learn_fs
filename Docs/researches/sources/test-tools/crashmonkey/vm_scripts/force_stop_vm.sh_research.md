# sources/test-tools/crashmonkey/vm_scripts/force_stop_vm.sh

Purpose: forcibly kills the local process for one numbered VM named `ubuntu16-vm<N>`.

Important APIs/types/functions: one argument `vm`, `ps aux`, `grep ubuntu16-vm"$vm"`, `cut`, and `kill`. Control flow validates one arg, prints a timestamped message, finds matching PID(s), and kills them.

State/persistence behavior: abrupt VM termination with possible dirty VM disk state. Dependencies/integration: used by restart scripts when VMs are unresponsive or read-only.

Risks/test signals: broad grep matching can return multiple or unintended PIDs, no check if no process is found, and no graceful VBoxManage poweroff is attempted.
