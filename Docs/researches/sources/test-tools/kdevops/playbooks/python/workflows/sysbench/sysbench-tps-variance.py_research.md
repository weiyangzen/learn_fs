# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-variance.py

Purpose: Computes TPS distribution statistics and generates multiple variance/dispersion plots for one or two sysbench outputs.

Key APIs and flow: `extract_tps()` collects decimal TPS samples; `analyze_tps()` returns mean, median, standard deviation, and variance; `print_statistics()` logs them. Plot functions create histograms, box plots, KDE density, combined histogram/density, normal bell curves, histogram plus bell curve, variance bars, and outlier scatter. `main()` parses optional second file, labels, output directory, colors, applies dark theme, and runs every plotter.

State, dependencies, integration: Reads text files and writes fixed-name images to `--dir`. Depends on numpy, matplotlib, seaborn, and scipy. It is a richer sysbench variability analyzer.

Risks and test signals: Several functions call `min(tps_values2)` before checking if the second dataset exists; `plt.show()` is called after saves; output path concatenates strings and expects trailing slash; empty datasets produce numpy warnings or failures. Tests should cover single-file mode, empty inputs, output dirs with/without slash, and zero-variance data.
