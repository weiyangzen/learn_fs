# sources/test-tools/fio/tickmarks.h

## Purpose
`tickmarks.h` exposes the tick mark data structure and calculation entry point used by fio graphing code.

## Important APIs, Types, and Functions
`struct tickmark` contains a numeric `double value` and a fixed `char string[20]` label. `calc_tickmarks()` returns the number of tick marks and allocates/fills an array through `struct tickmark **tm`; it also returns the selected power-of-ten scaling and supports K/M/G-style symbols.

## Control Flow and State
This header has no executable control flow. The ownership contract is important: callers receive heap storage and are responsible for releasing it.

## Dependencies and Integration Points
It is included by `tickmarks.c` and any graph/report code that consumes generated ticks. The struct string size is part of the interface.

## Risks and Test Signals
Risks include buffer-size constraints for labels, caller leaks if `tm` is not freed, and lack of documentation for invalid ranges. Signals are compile compatibility and correct axis labels in generated plots.
