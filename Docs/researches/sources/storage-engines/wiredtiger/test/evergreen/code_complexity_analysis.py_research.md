<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py

Purpose: converts Metrix++ complexity outputs into an Atlas-compatible JSON metric document for Evergreen code statistics tasks.

Important APIs: `get_atlas_compatible_code_statistics(summaryFile, dataFile, outfile)` wraps metrics under `Test Name: Code Complexity`. `get_code_complexity()` returns a list containing average complexity, range counts, and top regions. `get_region_list()` uses pandas `nlargest()` on `std.code.complexity:cyclomatic`. `get_complexity_ranges_list()` counts functions above 20, 50, and 90. `get_average()` parses the Metrix++ Python-formatted view output with `ast.literal_eval()` and extracts the aggregate cyclomatic average.

Control flow: `main()` requires `--summary`, optional `--outfile`, and `--data_file`, then writes JSON.

State and persistence: reads Metrix++ view text and CSV; writes the Atlas output, creating the parent directory if needed.

Dependencies and integration: called by `cyclomatic-complexity.sh` after Metrix++ collect/view/export. Depends on pandas and exact CSV column names.

Risks and test signals: `dataFile` is optional in argparse but required by the processing path. `get_average()` error text intends to include exception details but lacks f-string interpolation for `{e.text}`. Parsing uses Python literals rather than strict JSON because Metrix++ view emits Python-like output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py -->
