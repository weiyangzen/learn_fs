<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py

Purpose: measures verify workload behavior when prefetch is explicitly disabled.

Important APIs and functions: imports `microbenchmark_prefetch`, constructs `Operation.OP_VERIFY` with config `prefetch=(enabled=false)`, and uses `Workload`.

Control flow: instantiate base, populate data, close and reopen the connection to flush cache, reopen a session, define and call `run_workload`, run verify for 300 seconds, print/write prefetch stats, close resources.

State and persistence: data table persists across connection reopen. Reopen clears cache to make verify reads meaningful. Statistics are collected after the verify run and written to `prefetch_stats.out`.

Dependencies and integration: paired with `microbenchmark_prefetch_on_verify.py`; comparison expects fewer blocks read when prefetch is off.

Risks: full 12-million-row populate plus 5-minute verify is expensive. The table object is reused across reopen, relying on Workgen table URI state rather than live cursor/session state.

Test signals: verify `assert ret == 0`, printed "Start/Finished verifying", and lower blocks-read stats relative to the prefetch-on variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/microbenchmark_prefetch_off_verify.py -->
