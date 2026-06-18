# sources/storage-engines/leveldb/util/histogram.h

## Purpose
`histogram.h` declares the benchmark histogram class.

## Important APIs, Types, and Functions
`Histogram` exposes `Clear`, `Add`, `Merge`, and `ToString`; private helpers compute median, percentiles, average, and standard deviation.

## Control Flow
Callers construct a histogram, clear it before use, add samples, optionally merge other histograms, and render text output.

## State, Dependencies, and Integration
It stores min/max, count, sum, sum of squares, and fixed bucket counts. It depends only on `<string>` in the header.

## Risks and Test Signals
The constructor does not call `Clear`, so callers must initialize before use unless construction paths elsewhere do so. There are no direct tests in this subset.
