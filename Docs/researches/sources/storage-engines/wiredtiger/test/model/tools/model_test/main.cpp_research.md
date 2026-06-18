# sources/storage-engines/wiredtiger/test/model/tools/model_test/main.cpp

## Purpose
This is the standalone randomized/replay workload runner for the WiredTiger model. It can generate workloads, load workload files, run them in both the model and WiredTiger, compare per-operation return codes, verify final database contents in a child process, print workloads, preserve failures, and reduce counterexamples.

## Important APIs, Types, and Functions
Core functions are `run_and_verify`, `update_spec`, `load_spec`, `load_workload`, `reduce_counterexample_by_aspect`, `reduce_counterexample`, and `main`. Important types include `model::kv_workload`, `model::kv_workload_generator_spec`, `model::kv_workload_generator`, `model::kv_workload_runner_wt`, `model::kv_database`, `model::shared_memory`, `model::shared_memory`, `reduce_counterexample_context_t`, and the C `shared_verify_state` shared with the verifier subprocess.

## Control Flow
`main` parses CLI options for connection/table/generator config, seed, runtime/iteration bounds, workload length/table counts, print-only mode, preservation, and counterexample reduction. If workload files are supplied, it parses and runs each file. Otherwise it repeatedly generates workloads from a seeded generator until runtime and iteration criteria are met. `run_and_verify` runs the workload in the model, restarts the model to match recovery, writes `model_test.workload`, runs WT, compares return vectors, forks a verifier process, and checks the child exit status. On failure, `reduce_counterexample` tries to shrink the workload by sequences, tables, and operations.

## State, Persistence, and Integration
The tool creates and removes a WiredTiger home, optionally with a `kv_home` subdirectory for disaggregated storage. It writes the main workload file and may write `reduced.workload` in the failure home. It can merge connection and table configuration from command-line strings, config files, generated logging settings, and optional random timing stress settings. Verification opens the resulting WT database and compares every listed table with the model's expected state; disaggregated mode picks up the latest checkpoint first.

## Risks and Test Signals
This is a high-leverage testing tool, so determinism and diagnostics matter. Risks include mismatched model/WT return vector lengths, generated malformed workloads, failure reduction producing invalid schedules, unbounded core dumps during reduction, and config strings changing generator behavior unexpectedly. Strong signals are printed iteration/seed lines, exact operation index for return-code mismatch, child-process verification errors, saved reproducer workloads, and reduced counterexamples that still reproduce the failure.
