<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py

Purpose: formats Workgen workload latency statistics into human-readable text files or stdout, with optional ASCII plots.

Important APIs and functions: public `workload_latency(workload, outfilename=None, plot=False)`. Private helpers `_show_buckets`, `_latency_buckets`, `_latency_preprocess`, `_latency_plot`, `_latency_op_plot`, and `_latency_optype`.

Control flow: `workload_latency` opens an output file if requested, then processes workload stats for insert, checkpoint, read, remove, update, truncate, RTS, and not-found operations. `_latency_optype` skips empty operation types, prints totals/average/min/max, prints bucket totals, and optionally plots microsecond/millisecond/second histograms. Plotting preprocesses SWIG arrays by merging buckets and scaling into an 80-column by 20-row ASCII chart.

State and persistence: writes to the requested latency file or stdout. It reads `workload.stats` and does not mutate workload state except assigning `arr.height` in preprocessing.

Dependencies and integration: imported by `runner.__init__` and used across benchmark scripts to write `latency.out` or named RTS files.

Risks: output file is opened without explicit close when `outfilename` is used; process exit normally closes it, but long-lived import usage could leak. Assigning `height` to SWIG arrays may depend on permissive wrapper behavior. Bucket summaries print total counts rather than detailed bucket contents unless plot mode is true.

Test signals: existence/non-empty latency files and expected operation sections for nonzero stats.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/latency.py -->
