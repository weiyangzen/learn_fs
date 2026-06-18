# sources/security-integrity/gocryptfs/tests/stress_tests/extractloop_plot_csv.m

## Purpose
Octave plotting helper for visualizing `extractloop.bash` CSV output.

## Important APIs, Types, And Functions
- `csvread('/tmp/extractloop.csv')` loads runtime, RSS, and iteration duration rows.
- `plotyy` renders RSS in MiB and iteration time in seconds against runtime.
- Axes labels, line styles, grid, and a blocking `input` keep the figure visible.

## Control Flow
The script reads the CSV, opens a large figure, plots memory and duration on separate y axes, formats markers, draws immediately, and waits for Enter before exit.

## State And Persistence
Reads only `/tmp/extractloop.csv`; it writes no files.

## Dependencies And Integration Points
Depends on GNU Octave and the CSV shape produced by `extractloop.bash` as `N,SECONDS,RSS,delta`.

## Risks And Edge Cases
No validation is performed for missing, empty, or malformed CSV data. `plotyy` behavior can differ across Octave versions.

## Test Signals
A visible plot with RSS and iteration-time trends is the intended signal.
