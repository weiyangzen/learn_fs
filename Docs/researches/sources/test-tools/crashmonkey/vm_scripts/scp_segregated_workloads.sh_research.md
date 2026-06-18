# sources/test-tools/crashmonkey/vm_scripts/scp_segregated_workloads.sh

Purpose: copies pre-segregated workload directories to selected remote server nodes.

Important APIs/types/functions: args start server, end server, segregated workload path, `live_nodes`, `scp -r -i ~/crashmonkey.pem`, user `cc`, and destination `~/seq2/`.

Control flow: loops indexed IPs from `live_nodes`, skips outside the requested server range, and copies `$seg_path/node<i>-<ip>/*` to the node. State/persistence behavior: writes workload files into remote `seq2` directories.

Dependencies/integration: follows `segregate_workloads*` output layout. Risks/test signals: assumes node directory names include IP exactly, no destination cleanup here, no error handling, and unquoted glob/source issues.
