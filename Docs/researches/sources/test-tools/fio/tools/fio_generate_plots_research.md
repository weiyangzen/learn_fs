# sources/test-tools/fio/tools/fio_generate_plots

## Purpose
`fio_generate_plots` is a shell utility that turns fio log files into SVG graphs using gnuplot. It generates latency, IOPS, submission latency, completion latency, and bandwidth plots.

## Important APIs, Types, and Functions
The script takes a required subtitle/title and optional `xres yres`. It finds `gnuplot`, sets many default gnuplot snippets for colors, terminal, fonts, axes, range, grid, key, and source label, then defines `plot()`. `plot()` scans for files matching `*_<tag>.log` and `*_<tag>.*.log`, extracts a queue-depth label from the filename, builds a gnuplot `plot` expression using time column `$1/1000` and scaled value column `$2/SCALE`, and writes `$TITLE-$FILETYPE.svg`.

## Control Flow and State
Global shell variables hold title, resolution, `SAMPLE_DURATION`, default plot commands, and the currently accumulated `PLOT_LINE`. The script calls `plot()` five times with different tags and y-axis scales.

## Dependencies and Integration Points
It depends on POSIX shell, gnuplot 4.4+, fio log naming conventions, and SVG-capable viewers. It consumes fio logs created by `write_*_log` options.

## Risks and Test Signals
Risks include unquoted filename/title handling, brittle queue-depth extraction, a likely unused/undefined `DEFAULT_GRID_LINE` variable in `DEFAULT_OPTS`, hard-coded data-source label, and exit on first missing plot family. Signals are generated SVG files and gnuplot errors.
