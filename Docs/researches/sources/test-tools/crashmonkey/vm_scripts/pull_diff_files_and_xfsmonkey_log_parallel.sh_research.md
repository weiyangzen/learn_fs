# sources/test-tools/crashmonkey/vm_scripts/pull_diff_files_and_xfsmonkey_log_parallel.sh

Purpose: launches batched background collectors for diff files and XFSMonkey logs across multiple servers.

Important APIs/types/functions: args `run`, `batch_size`, `num_servers`, loop variables `st`/`end`, `nohup ./pull_diff_files_and_xfsmonkey_log.sh ... > out<i>.log &`.

Control flow: computes server ranges of `batch_size` and starts one collector process per range until all servers are covered. State/persistence behavior: creates background jobs and per-batch logs; actual artifact collection is delegated.

Dependencies/integration: wrapper around the nonparallel pull script. Risks/test signals: no wait/join or failure aggregation, overlapping output directories can race, and `end` can exceed `num_servers`.
