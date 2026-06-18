# sources/test-tools/crashmonkey/vm_scripts/vm_remote_progress_script.sh

Purpose: reports progress of a remote XFSMonkey run by scraping logs, workload count, diff count, and RAM disk errors.

Important APIs/types/functions: reads `/home/user/projects/crashmonkey/xfsmonkey*.log`, greps `Test` and `Error inserting RAM disk module`, counts `build/xfsMonkeyTests/j-lang*`, counts diff results, and prints host plus metrics.

Control flow: assigns `completed`, `ram_disk_error`, `total`, and `num_diffs`, then echoes a formatted one-line status. State/persistence behavior: read-only.

Dependencies/integration: remote operator status script. Risks/test signals: glob failures and missing logs can produce noisy errors; `completed` parsing assumes exact log format.
