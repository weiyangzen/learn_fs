# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script.sh

Purpose: runs a named remote script with sudo on every local NAT-forwarded VM.

Important APIs/types/functions: one argument `remote_script`, environment `num_vms`, `rsh -p`, fixed password piped to `sudo -S bash`, and ports from 3022.

Control flow: validates one arg, loops VMs, prints a banner, runs the remote script, and increments the port. State/persistence behavior: depends entirely on the remote script; this wrapper initiates remote side effects.

Dependencies/integration: generic trigger for the VM farm. Risks/test signals: hard-coded password, command quoting permits argument/shell issues, no failure handling, and rsh is insecure.
