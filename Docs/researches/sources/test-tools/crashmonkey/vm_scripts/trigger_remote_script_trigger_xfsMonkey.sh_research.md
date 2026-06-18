# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey.sh

Purpose: starts `vm_remote_trigger_script.sh` for a given filesystem on each local NAT-forwarded VM in the background, then checks process status.

Important APIs/types/functions: arg `fs`, environment `num_vms`, `rsh`, `nohup`, `sudo -S`, remote `/home/user/vm_remote_trigger_script.sh`, `ps aux | grep -e xfsMonkey -e vm_remote_trigger`, and sleeps.

Control flow: validates filesystem arg, loops VMs, launches remote trigger with output to `trigger_<fs>.log`, sleeps 10 seconds, checks remote processes, sleeps 5 seconds, and increments port. State/persistence behavior: starts long-running remote CrashMonkey tests.

Dependencies/integration: used to fan out XFSMonkey runs across local VMs. Risks/test signals: complex nested quoting/backgrounding, hard-coded password/user, and no verification that the background job actually survives after the shell exits.
