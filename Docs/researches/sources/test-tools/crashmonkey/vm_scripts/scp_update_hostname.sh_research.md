# sources/test-tools/crashmonkey/vm_scripts/scp_update_hostname.sh

Purpose: copies `update_hostname.sh` to VM numbers 9 through 16 using NAT SSH ports 3030 through 3037.

Important APIs/types/functions: fixed port start 3030, loop `seq 9 16`, `scp -P`, and destination `user@127.0.0.1:~/`.

Control flow: loops VM numbers, copies the script, increments port. State/persistence behavior: writes the hostname update script into selected VM home directories.

Dependencies/integration: older/specialized hostname setup helper. Risks/test signals: hard-coded VM range and ports, no password automation or error handling.
