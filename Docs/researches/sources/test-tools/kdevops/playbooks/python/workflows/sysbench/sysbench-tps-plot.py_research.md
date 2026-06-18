# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-plot.py

Purpose: Generates a single TPS-over-time plot from sysbench text output.

Key APIs and flow: `parse_line()` uses the same sysbench TPS regex as the comparator. `main()` reads the input file, parses lines through a `ThreadPoolExecutor`, exits on file-not-found or no TPS samples, switches the time axis to hours for long runs, constructs a DataFrame, plots points, and writes the output image.

State, dependencies, integration: Reads one text file and writes one PNG by default. Depends on pandas and matplotlib. It is a direct post-processing utility for sysbench workflow logs.

Risks and test signals: The help says text or JSON, but only text lines are parsed; broad use of `exit(1)` rather than `sys.exit`; no theme/backend selection; regex requires decimal TPS. Tests should cover valid logs, empty logs, integer TPS formats, long runs, and missing input.
