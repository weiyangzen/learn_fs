# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_range.sh

Purpose: triggers XFSMonkey runs only for a selected VM index range.

Important APIs/types/functions: args filesystem, start VM, end VM, environment `num_vms`, `rsh`, `sudo -S`, remote `vm_remote_trigger_script.sh`, and ports from 3022.

Control flow: loops all VM indices, skips those outside range while still advancing port, runs the remote trigger synchronously for included VMs, sleeps one second, and increments port. State/persistence behavior: starts or runs remote CrashMonkey workflows on selected VMs.

Dependencies/integration: used by the parallel trigger wrapper. Risks/test signals: no backgrounding here, so long remote runs can serialize per VM in a batch; hard-coded password and no failure capture.
