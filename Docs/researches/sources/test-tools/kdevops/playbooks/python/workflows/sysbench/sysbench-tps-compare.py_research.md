# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-compare.py

Purpose: Compares two sysbench text outputs by plotting transactions per second over time.

Key APIs and flow: `parse_line()` extracts `[ Ns ] ... tps: X` samples with regex. `read_sysbench_output()` parses all lines concurrently using `ThreadPoolExecutor`. `main()` supports optional input files, legends, matplotlib theme, output path, theme listing, and report interval scaling. It converts the x-axis to hours for runs longer than two hours, builds two pandas DataFrames, and saves an overlay scatter plot.

State, dependencies, integration: Reads two text files and writes one image. Depends on pandas and matplotlib. Used for sysbench A/B comparisons, with defaults tuned for MySQL doublewrite tests.

Risks and test signals: Empty parsed data causes `max()` failures; report interval multiplies already reported timestamps, which may be wrong if timestamps are absolute; no file-not-found handling. Tests should cover empty files, theme listing, long runs, report interval semantics, and irregular sysbench lines.
