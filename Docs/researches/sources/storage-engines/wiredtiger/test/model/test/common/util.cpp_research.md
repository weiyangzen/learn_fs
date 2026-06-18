# sources/storage-engines/wiredtiger/test/model/test/common/util.cpp

Purpose: implements general model test utilities, including temp file creation, time/range/string helpers, debug-log verification, and workload model-vs-WT verification.

Important APIs and functions: `create_tmp_file`, `current_time`, `parse_uint64_range`, `trim`, `verify_using_debug_log`, and `verify_workload`.

Control flow: `create_tmp_file` builds a `mkstemps` template, creates/closes the file, and returns the path. `verify_using_debug_log` opens WT with logging, lists tables, loads a model from the live debug log, verifies each table, compares timestamps, prints the debug log to JSON, loads another model from JSON, verifies again, optionally injects a bogus model row to prove verification can fail, then closes session/connection. `verify_workload` runs the workload in the model, restarts the model to mimic recovery, recreates the WT home, runs the workload in WT, compares return-code vectors, opens WT, verifies all tables, and closes.

State and persistence: creates temporary JSON files and WT homes. Verification creates transient `kv_database` instances and opens/closes WT resources.

Dependencies and integration: includes `debug_log_parser.h`, `model/test/util.h`, `model/test/wiredtiger_util.h`, and `model/util.h`; uses `test_util.h` WT open/recreate helpers.

Risks: temp file paths use `alloca` and fixed suffix template assumptions. Debug-log verification requires logging enabled and no second WT instance mutating the database while printing. The negative verification path only works for string-key tables. `verify_workload` assumes model restart semantics line up with WT recovery.

Test signals: this file is the main integration signal for workload correctness and debug-log parser correctness: return-code equality, table verification success, timestamp equality, and intentional verification failure.
