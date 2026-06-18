# sources/test-tools/fio/t/btrace2fio.c

## Purpose
Converts binary Linux blktrace streams into either an ASCII workload summary or a fio replay-style job file. It groups observed I/O by trace PID, infers read/write/trim mix, block-size distribution, queue depth, sequentiality, start delay, runtime, rate, target devices, and optional collapsed `numjobs`.

## Important APIs, Types, and Functions
Core state is held in `struct btrace_pid` and `struct btrace_out`; block-size accounting uses `struct bs`, device mappings use `struct trace_file`, and in-flight queue-depth tracking uses `struct inflight`. `load_blktrace()` reads `struct blk_io_trace` records through a fio `fifo`; `handle_trace()`, `handle_queue_trace()`, `handle_trace_fs()`, and `handle_trace_discard()` update per-PID statistics. `trace_needs_swap()` and `byteswap_trace()` handle endianness. `__output_p_ascii()` and `__output_p_fio()` emit the two output formats, while `prune_entry()`, `entries_close()`, `merge_entries()`, and `check_merges()` filter or collapse similar jobs.

## Control Flow
`main()` parses thresholds and output options, detects trace byte order, initializes PID and in-flight hash buckets, loads one trace file, normalizes the first timestamp, then calls `output_p()`. While loading, queue actions create in-flight entries and update size/count/sequential stats, merge actions adjust or remove in-flight entries, and completion actions convert bytes to KiB and reduce outstanding depth. Output pruning drops tiny, short, or low-rate PIDs before sorting by I/O count and rendering each retained PID as a summary or fio job section.

## State and Persistence Behavior
The program is batch-only. Persistent output is stdout text; there is no file write besides caller redirection. In-memory state includes global hash lists, dynamic block-size arrays, per-PID device names, merged PID lists, and optional extra fio options. `filename` supplied with `-d` overrides detected devices for fio job output.

## Dependencies and Integration Points
Depends on fio internals for data-direction constants, intrusive lists, hashes, fifos, byte swapping, logging, min/max helpers, blktrace record definitions, and Linux device lookup. Generated fio output integrates with fio job-file syntax through `ioengine`, `iodepth`, `rw`, `rwmixread`, `percentage_random`, `filename`, `runtime`, `bssplit`, `rate`, and user-provided `-a` options.

## Risks
Depth inference depends on matching queue/merge/complete trace events; missing completions cap depths at `max_depth`. Device lookup failure is fatal for fio job output unless `-d` is used. Low-frequency block sizes below one percent are omitted from `bssplit`, which can hide tail behavior. Collapse heuristics compare sequentiality and depth only, so merged jobs can overgeneralize distinct workloads. Several allocations are unchecked or only lightly checked.

## Test Signals
Useful signals are successful parsing of native and swapped traces, rejection of bad magic/version/PDU lengths, sane ASCII totals, replay job output for read/write/trim and mixed jobs, `-d` override behavior, pruning thresholds, rate emission, and collapse behavior on near-identical PIDs.
