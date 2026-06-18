# sources/test-tools/fio/tools/hist/fiologparser_hist.py

Purpose: Python 3 CLI that converts fio `*_clat_hist*` latency histogram logs into interval statistics: end time, sample count, min, average, median, configurable percentiles, and max. It supports mixed or per-direction output (`r`, `w`, `t`, `m`), coarse fio histogram bin layouts, weighted interval accounting, optional job-file interval discovery, and unit conversion through divisors/us-bin mode.

Important APIs/functions: `HistFileRdr` is a simple line reader for unweighted processing. `weighted_percentile()`, `weights()`, and `weighted_average()` implement weighted histogram math. `_plat_idx_to_val()` mirrors fio's platform histogram bin conversion and `plat_idx_to_val_coarse()` adapts reduced/coarsened bins. `histogram_generator()` merges chunked pandas readers in timestamp order. `process_interval()` and `process_weighted_interval()` aggregate bins into output rows. `main()` owns option normalization, column detection, bin-value initialization, direction selection, and output mode dispatch.

Control flow: CLI arguments are parsed, optional fio job config is scanned for `log_hist_msec`, output columns are generated, the first input line determines histogram column count and coarseness, then either unweighted interval aggregation or weighted interval aggregation runs. Weighted mode buffers rows until enough future data exists to account for latency overlap across interval boundaries.

State/persistence: global `percs`, `columns`, histogram column counts, and bin-value arrays are initialized once per run. The script reads log files only and writes CSV-like rows to stdout; warnings go to stderr. It does not write persistent state.

Dependencies/integration: depends on `pandas` and `numpy`; fio-specific integration is the expected log format of time, direction, block size, histogram bins and the histogram math from fio `stat.c`. The `--job-file` parser still uses legacy `SafeConfigParser/readfp` compatibility.

Risks/test signals: risks include `e.message` on `ValueError` not being portable in Python 3, memory growth from repeated `np.append()` in weighted mode, divide-by-zero if all weights are zero, and mis-detection if the first input line is malformed. Good tests would cover empty files, coarseness detection, weighted zero-length samples, direction splits, epoch timestamps, and old microsecond-bin logs.
