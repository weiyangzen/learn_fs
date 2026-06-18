# sources/test-tools/crashmonkey/vm_scripts/scp_file_to_vms.sh

Purpose: copies one local file to the home directory of every local NAT-forwarded VM.

Important APIs/types/functions: one argument `file_to_scp`, environment `num_vms`, `scp -P`, user `user@127.0.0.1`, and ports from 3022.

Control flow: validates one arg, loops VM count, scps the file, and increments port. State/persistence behavior: writes a copy of the file into each VM home directory.

Dependencies/integration: ad hoc distribution helper. Risks/test signals: no password automation here unlike other scripts, no error handling, and unquoted file path can fail on spaces.
