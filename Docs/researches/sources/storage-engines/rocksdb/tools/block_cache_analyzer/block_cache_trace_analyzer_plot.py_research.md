<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py

## Purpose

`block_cache_trace_analyzer_plot.py` converts CSV outputs from the C++ block-cache trace analyzer and Python simulator into PDF graphs. It handles miss-ratio curves, LRU-relative diffs, access timelines, stacked bucket summaries, reuse graphs, percentage access summaries, skew graphs, correlation heatmaps, and Python-simulator byte-miss statistics.

## Important APIs, Types, And Functions

`get_cmap()` initializes a large shuffled color palette. Global `bar_color_maps`, `colors`, and `color_index` keep label colors stable across graphs.

`num_to_gb()` formats numeric byte counts as GiB text, though it is not used in the visible code paths.

`plot_miss_stats_graphs()` and `plot_miss_stats_diff_lru_graphs()` read MRC-like CSVs with rows of `cache_name,num_shard_bits,ghost_capacity,capacity,value`. They generate capacity-vs-value plots and value differences relative to `lru-0-0`.

`sanitize()` strips leading underscores from labels and replaces the uint64 max sentinel with `max`.

`read_data_for_plot_vertical()` and `read_data_for_plot_horizontal()` parse two CSV orientations into `x`, `labels`, and `label_stats`. `read_data_for_plot()` selects between them.

`plot_line_charts()` writes multi-page PDF line charts. `plot_stacked_bar_charts()` writes stacked bar charts. `plot_heatmap()` writes seaborn heatmaps from correlation output.

Higher-level functions dispatch graph families: `plot_timeline()`, `plot_correlation()`, `plot_reuse_graphs()`, `plot_percentage_access_summary()`, `plot_access_count_summary()`, and `plot_miss_ratio_timeline()`.

The `__main__` block expects an input directory containing experiment subdirectories and an output graph directory. It iterates each experiment directory, creates a matching output subdirectory, and calls all graph-family functions.

## Control Flow

The script imports matplotlib with the `Agg` backend for headless PDF generation. On execution, it validates two CLI arguments, lists the input directory, and skips entries that are not directories.

For each experiment subdirectory, it processes analyzer CSVs by suffix/prefix. Some graph functions open a `PdfPages` object and add one page per matching CSV file. Correlation processing first scans `*_correlation_input` files, computes Spearman correlations with pandas, writes `*_correlation_output`, and then plots those outputs as heatmaps.

The plotting contract depends heavily on filename suffixes from `block_cache_trace_analyzer.cc`, `block_cache_pysim.py`, and `block_cache_pysim.sh`.

## State And Persistence Behavior

The script writes PDF files under the output graph directory, preserving experiment subdirectory names. It also writes derived `*_correlation_output` CSV files back into the input CSV directories.

Global color state persists across all plots in a process. This helps keep a label's color stable, but it also means color assignment depends on processing order and can eventually exhaust the fixed 360-color list if many unique labels are seen.

## Dependencies And Integration Points

Runtime dependencies include Python standard modules plus `matplotlib`, `numpy`, `pandas`, and `seaborn`. It uses `matplotlib.backends.backend_pdf.PdfPages` and explicitly selects the non-interactive `Agg` backend.

The script is the consumer for CSVs emitted by the C++ analyzer (`mrc`, access timelines, reuse summaries, percentage summaries, skewness, correlation inputs) and for Python simulator aggregates (`ml_*_avgmb`, `ml_*_p95mb`, `ml_*_mrc`, and ML timelines).

## Risks And Edge Cases

The script uses older matplotlib/pandas APIs in places. `plt.xscale("log", basex=2)` is incompatible with newer matplotlib versions that use `base=2`, and `DataFrame.pivot("label", "corr", "value")` is incompatible with newer pandas keyword-only signatures.

`plot_miss_ratio_timeline(csv_result_dir, output_result_dir)` is called from the experiment loop with the top-level directories rather than the current experiment subdirectory, unlike other plot functions. This can cause missed files or output in the wrong directory.

`plot_miss_ratio_timeline()` calls the same miss-timeline plot twice with identical parameters, overwriting or duplicating work.

Line plotting uses `[int(x[i]) for i in range(len(x) - 1)]` and `label_stats[label_index][:-1]`, dropping the last x and y value. This may be intentional to avoid an open-ended bucket, but for timeline data it can silently omit real data.

Input parsing assumes non-empty CSVs and numeric values in all data cells. Empty files, headers only, NaNs outside correlation paths, or labels exceeding the color list can fail.

## Test Signals

There are no direct tests in this subset. The strongest validation signals would be golden CSV fixtures from the analyzer and simulator, smoke tests that generate PDFs with current matplotlib/pandas versions, and checks that each expected PDF appears under the correct experiment output directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_plot.py -->
