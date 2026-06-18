# sources/test-tools/fio/tools/plot/fio2gnuplot

Purpose: Python 2/3-compatible CLI that transforms fio bandwidth or IOPS logs into intermediate data files, summary statistics, and gnuplot scripts/images. It can select files by glob or predefined `_bw.log`/`_iops.log` patterns, aggregate traces, compute min/max/average/stddev files, optionally render gnuplot, and query prior `.global` summaries.

Important APIs/functions: `find_file()` performs local pattern selection. `compute_temp_file()` reads selected fio logs in lockstep, filters by time range, captures block size, and writes `gnuplot_temp_file.*`. `compute_aggregated_file()` concatenates temp files. `compute_math()` writes `.average`, `.min`, `.max`, `.stddev`, `.global`, and `mymath`. `generate_gnuplot_script()` writes `mygraph` plus compare scripts. `render_gnuplot()` shells out to `gnuplot`. `main()` parses getopt options and orchestrates selection, transformation, math, graph script generation, rendering, and cleanup.

Control flow: after locating fio `*.gpm` templates in `/usr/share/fio/` or `/usr/local/share/fio/`, options determine pattern/title/output paths. Matching logs are sorted, mode is inferred from filename, output basename may be derived from user glob, then global parsing or full data processing runs.

State/persistence: creates many files in the output directory: temp data, aggregate output, math summaries, graph scripts, and optional PNGs. Global lists `temporary_files`, `keep_temp_files`, and `verbose` coordinate cleanup and logging.

Dependencies/integration: uses standard Python plus `six`, filesystem gpm templates, and an external `gnuplot` executable. Expects fio log lines with at least time, performance, and block-size fields.

Risks/test signals: uses `os.system()` with output directory interpolation, has sparse error handling, and `average()` will divide by zero if a trace contributes no samples after filtering. Tests should cover no-match fallback for per-job logs, custom output dir cleanup, min/max filters, multi-file compare script content, missing gpm files, and global summary parsing.
