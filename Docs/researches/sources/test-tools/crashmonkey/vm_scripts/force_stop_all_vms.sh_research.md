# sources/test-tools/crashmonkey/vm_scripts/force_stop_all_vms.sh

Purpose: forcibly kills local processes whose command line matches `startvm`, stopping running VirtualBox VMs at the process level.

Important APIs/types/functions: `ps aux`, `grep startvm`, `cut`, and `kill`. Control flow loops over matching PIDs and kills each.

State/persistence behavior: abruptly terminates VM processes and can leave VM state unclean. Dependencies/integration: emergency operator utility paired with start/stop scripts.

Risks/test signals: process matching is broad and could kill unrelated commands containing `startvm`; no confirmation or graceful shutdown is attempted.
