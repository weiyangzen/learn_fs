# sources/test-tools/crashmonkey/vm_scripts/vm_remote_check_running.sh

Purpose: remote VM status helper that reports whether any `xfsMonkey` process is running.

Important APIs/types/functions: `ps aux`, `grep xfsMonkey`, `wc -l`, `uname -n`, and conditional echo. Control flow counts matching processes and prints either no run or some run in progress.

State/persistence behavior: read-only process inspection. Dependencies/integration: can be triggered remotely by operator scripts.

Risks/test signals: process matching may count unrelated grep-like command lines except it excludes grep; it does not check `c_harness` or remote trigger scripts.
