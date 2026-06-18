<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py

Purpose: minimal Workgen example showing context setup, table creation, insert operations, repeated operation multiplication, workload execution, and optional verbose table display.

Important APIs and functions: defines `show(tname, s, args)` to print table contents when `--verbose` is set. Uses `Context.wiredtiger_open`, `Session.create`, `Table`, `Key.KEYGEN_APPEND`, `Value`, `Operation.OP_INSERT`, `Thread`, and `Workload`.

Control flow: open a 1 GB cache WT home through `Context`; create `table:simple`; run one insert workload; optionally print contents; run another workload with five repeated inserts; print again.

State and persistence: data persists in the temporary/default Workgen home for the script. `Context` handles home cleanup unless command-line options override it. No latency file is generated.

Dependencies and integration: demonstrates runner initialization and Workgen basics; intended as a direct example rather than perf workload.

Risks: verbose output can be noisy if repetition is increased. Uses `from runner import *` and Workgen globals for simplicity.

Test signals: two `assert ret == 0` checks and visible inserted records under `--verbose`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/example_simple.py -->
