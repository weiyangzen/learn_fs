# sources/storage-engines/foundationdb/contrib/export_graph.py

## Purpose
Plots a DDSketch latency distribution from JSON, either interactively or to a PNG file.

## Important APIs, Types, And Functions
CLI arguments are `--txn`, `--file`, optional `--title`, `--savefig`, and `--op`. It uses `ddsketch_calc.DDSketch` to convert bucket indices to approximate latency values and Matplotlib to render the line plot.

## Control Flow
The script loads JSON, extracts `data[txn][op]["buckets"]` and `errorGuarantee`, trims leading/trailing zero buckets, maps bucket indices to values, configures axis formatting and labels, then saves or shows the plot.

## State And Persistence
Reads one JSON file and optionally writes a PNG. No other persistent state.

## Dependencies And Integration
Depends on Matplotlib, local `ddsketch_calc`, and the expected FoundationDB DDSketch JSON schema.

## Risks
The code references `args.t`, but argparse defines `args.txn`; as written this raises `AttributeError`. `--op` is optional but required by indexing. All-zero buckets make `ls[0]` and `ls[-1]` fail. Input file is not closed explicitly.

## Test Signals
Test a minimal non-empty sketch with `--savefig`, all-zero buckets, missing operation, the `args.txn` path, and visual smoke tests for axis values.
