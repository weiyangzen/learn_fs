# sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log.sh

Purpose: collects diff result files and XFSMonkey logs from a selected server range and all VMs on each server.

Important APIs/types/functions: args `run`, `st`, `end`, directories `$run/diff_files` and `$run/xfsmonkey_logs`, `live_nodes`, fixed `num_vms=12`, `sshpass scp`, user `user`, password `password`, NAT ports starting at 3022.

Control flow: creates output directories, iterates IPs from `live_nodes` with server index, skips outside the requested range, then loops VM ports to scp diff files and one log per VM with a server/vm-specific name.

State/persistence behavior: creates local collection directories and copies remote artifacts. Dependencies/integration: used after distributed XFSMonkey runs.

Risks/test signals: hard-coded credentials, unquoted paths, fixed VM count, no scp failure handling, and copying all diff files into one directory can collide on names.
