# sources/test-tools/crashmonkey/vm_scripts/vm_remote_kill_all_running.sh

Purpose: kills all remote `xfsMonkey` and `c_harness` processes inside a VM.

Important APIs/types/functions: `ps aux`, `grep -e xfsMonkey -e c_harness`, PID extraction, and `sudo kill -9`. Control flow loops over matching PIDs and force kills each.

State/persistence behavior: terminates active tests abruptly and may leave mounts/modules/diffs in partial state. Dependencies/integration: emergency cleanup helper.

Risks/test signals: broad process matching, hard-coded password, no graceful cleanup, and no follow-up module unmount cleanup.
