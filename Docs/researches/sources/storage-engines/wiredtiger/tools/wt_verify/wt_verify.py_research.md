# sources/storage-engines/wiredtiger/tools/wt_verify/wt_verify.py Research

## Purpose

`wt_verify.py` wraps the WiredTiger `wt verify -t` tool and parses its `dump_pages` or `dump_blocks` diagnostic output into structured dictionaries, optional pretty text, and interactive visualizations. It supports row-store and variable-length column-store output and is meant for inspecting page metadata, block allocation, free gaps, and checkpoint-level page distributions.

## Important APIs, Types, and Functions

Parsing is split by dump type. `parse_dump_pages()` reads checkpoint sections separated by `SEPARATOR`, delegates checkpoint headers to `parse_chkpt_info()`, and page bodies to `parse_node()` plus `parse_metadata()`. `parse_dump_blocks()` extracts root and address ranges into `{checkpoint: {page_type: [(offset, size), ...]}}`. `is_int()` performs opportunistic integer conversion.

Visualization functions include `show_block_distribution_broken_barh()`, `show_block_distribution_hist()`, `show_free_block_distribution()`, `histogram()`, `pie_chart()`, `visualize_chkpt()`, and `visualize()`. They use `matplotlib`, `numpy`, `pandas`, and `mpld3.serve` to create browser-served HTML. Execution helpers include `find_wt_exec_path()`, `construct_command(args)`, and `execute_command(command, output_file)`. `output_pretty()` serializes parsed dictionaries into a custom brace-heavy string.

## Control Flow

`main()` parses `--dump` as `dump_blocks` or `dump_pages`, optional filename/home/input/output/print/visualize/wt path flags, and either uses an existing input file or constructs and runs a `wt` command. Generated `wt` output is always written to `wt_output_file.txt`, then parsed. Dump-pages mode can write pretty output and optionally serve requested histograms/pie charts. Dump-blocks mode always builds three visualizations and serves them, regardless of `--visualize`. If no parsed data exists, it prints a no-data message and returns.

## State and Persistence Behavior

The wrapper may create or overwrite `wt_output_file.txt` in the current directory and may write a user-specified parsed output file. It starts a WebAgg/mpld3 server for visualization. It does not modify WiredTiger data, but it runs `wt verify` against the requested home and file.

## Dependencies and Integration Points

The script depends on a local `wt` executable, either supplied by `-wt` or discovered under the WiredTiger root relative to the script. It depends on stable textual formats from `wt verify -t -d dump_pages` and `dump_blocks`. Python dependencies are substantial: `numpy`, `pandas`, `matplotlib` with WebAgg, `mpld3`, and standard `argparse`, `subprocess`, `json`, `re`, and `operator.itemgetter`.

## Risks and Edge Cases

`construct_command()` builds a shell command string and `execute_command()` runs it with `shell=True`; although the filename is quoted, `home_dir`, `dump`, and `wt_exec_path` are interpolated directly, so untrusted arguments are unsafe. `parse_metadata()` uses `dict` as a local name and assumes metadata split patterns are exact. Some parsing errors are hard exceptions, which is appropriate for diagnostics but brittle across output changes. `show_block_distribution_hist()` uses `all_addr` after loops and will fail if data has no page entries. `histogram()` assumes both internal and leaf lists have data; empty DataFrames can fail on `describe().loc[...]`. Visualization calls can block by serving HTML, which is expected for an interactive tool but not ideal for automated runs.

## Test Signals

Fixtures should cover both dump formats, multiple checkpoints, root-only or empty trees, VLCS/row-store page types, address gap calculations, malformed separator/header lines, and visualization paths with missing internal or leaf pages. Security-oriented tests should validate command construction with spaces and shell metacharacters, or motivate replacing `shell=True` with an argument vector.
