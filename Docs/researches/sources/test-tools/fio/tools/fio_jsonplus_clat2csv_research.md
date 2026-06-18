# sources/test-tools/fio/tools/fio_jsonplus_clat2csv

## Purpose
`fio_jsonplus_clat2csv` converts fio `json+` latency histogram bins into per-job CSV files, including per-duration counts, cumulative counts, and percentiles for read, write, and trim submission/completion/total latencies.

## Important APIs, Types, and Functions
Constants `DDIR_LIST` and `LAT_LIST` define the output matrix. `parse_args()` accepts source JSON, destination stub, `--debug`, and `--validate`. `percentile()` computes cumulative fraction for a bin index. `more_bins()` drives a multi-list merge across latency streams. `get_csvfile()` appends `_jobN` to the destination. `validate()` reconstructs bins from generated CSV files and compares them to JSON bin dictionaries. `main()` loads JSON, builds column labels, optionally validates, otherwise creates one CSV per job.

## Control Flow and State
For each job, the script builds sorted `[nsec, count]` lists for each direction/latency pair, precomputes cumulative totals, then repeatedly emits the smallest remaining latency across all streams. Missing streams produce blank CSV fields.

## Dependencies and Integration Points
It depends on Python 2/3 compatibility helpers from `six`, fio `json+` output shape, and filesystem access for generated CSVs. It integrates with validation workflows that compare CSV output back to source JSON.

## Risks and Test Signals
Risks include assuming `jsondata['jobs'][job][ddir]` exists for all directions, large memory use for huge histograms, exact string comparison of CSV headers in validation, and a hard-coded large initial `min_lat`. Signals are generated `_jobN.csv` files, validation messages, and assertion/mismatch failures.
