# sources/test-tools/crashmonkey/vm_scripts/vm_remote_clear_diffs.sh

Purpose: removes all remote CrashMonkey diff result files inside a VM.

Important APIs/types/functions: `rm -r /home/user/projects/crashmonkey/diff_results/*`. Control flow is a single command.

State/persistence behavior: destructively deletes diff artifacts. Dependencies/integration: remote cleanup helper.

Risks/test signals: no existence check, no quoting, and running as a user with unexpected path layout can fail or delete unintended glob matches.
