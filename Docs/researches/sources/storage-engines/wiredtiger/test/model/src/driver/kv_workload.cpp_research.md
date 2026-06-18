# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload.cpp

Purpose: implements parsing, validation, and execution dispatch for text-serializable key/value workloads.

Important APIs and functions: `operation::parse` parses `name(arg,...)` strings with quote/escape handling and constructs the matching operation variant. It supports transaction lifecycle, checkpoints/crashes/restart/RTS, table creation, get/insert/remove/truncate, timestamps, and WT/model config operations. `kv_workload::assert_timestamps` validates monotonic stable/oldest timestamps, operation timestamps relative to stable, and disaggregated stable-timestamp requirements. `kv_workload::verify` checks table existence, updates table visibility after disaggregated crash/checkpoint behavior, and tracks checkpoint timestamp restoration. `run` executes against the model runner; `run_in_wiredtiger` executes against the WT runner.

Control flow and state: workload is a deque of `kv_workload_operation` entries, each carrying an operation variant and optional sequence number. Verification simulates metadata state enough to catch invalid references before execution.

Dependencies and integration: includes `kv_workload.h`, model and WT workload runners, `parse_uint64`, and WiredTiger constants.

Risks and test signals: parser currently assumes unsigned numeric keys/values for text input. `get` values are not yet compared (`FIXME-WT-14863`). A valid workload should pass `verify`, run in both model and WT, and produce comparable return-code streams.
