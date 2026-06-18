# sources/test-tools/crashmonkey/vm_scripts/vm_remote_update_hostname_script.sh

Purpose: remote VM hostname update script equivalent to `update_hostname.sh`.

Important APIs/types/functions: one argument `num`, constructed hostname `ubuntu16-vm<num>`, write `/etc/hostname`, `sed -i` in `/etc/hosts`, and `sudo hostname`.

Control flow: validates one arg, sets the hostname files and runtime hostname. State/persistence behavior: mutates system identity inside the VM.

Dependencies/integration: invoked by `trigger_remote_script_update_hostname.sh`. Risks/test signals: assumes `ubuntu16-vm1` appears in `/etc/hosts`, requires root privileges, and has no verification after setting.
