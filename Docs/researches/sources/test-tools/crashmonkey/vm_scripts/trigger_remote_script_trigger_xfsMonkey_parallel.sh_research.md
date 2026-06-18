# sources/test-tools/crashmonkey/vm_scripts/trigger_remote_script_trigger_xfsMonkey_parallel.sh

Purpose: launches batched background trigger scripts to start XFSMonkey across VM ranges.

Important APIs/types/functions: args `fs` and `batch_size`, environment `num_vms`, range variables, and `nohup ./trigger_remote_script_trigger_xfsMonkey_range.sh ... > out_trigger_log_<fs>_<st>_<end>.log &`.

Control flow: validates args, partitions VM indices into batches, starts one range trigger per batch, and increments the range. State/persistence behavior: creates local logs and starts remote XFSMonkey jobs via child scripts.

Dependencies/integration: parallel wrapper for the range trigger script. Risks/test signals: no wait/failure aggregation, potential overlapping VM ranges if arguments are wrong, and background jobs can overload local/remote resources.
