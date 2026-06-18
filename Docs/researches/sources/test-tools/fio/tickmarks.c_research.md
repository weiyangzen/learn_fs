# sources/test-tools/fio/tickmarks.c

## Purpose
`tickmarks.c` computes human-friendly graph tick labels for fio plotting code using a Graphics Gems-style nice-number algorithm.

## Important APIs, Types, and Functions
`nicenum(double x, int round)` chooses 1, 2, 5, or 10 times a power of ten for ranges and tick spacing. `calc_tickmarks(double min, double max, int nticks, struct tickmark **tm, int *power_of_ten, int use_KMG_symbols, int base_offset)` computes graph min/max, spacing, fractional formatting, allocates an array of `struct tickmark`, fills values and labels, then calls `shorten()`. `shorten()` detects common trailing zeros and optionally replaces them with K/M/G/P/E suffixes, adjusting `power_of_ten`.

## Control Flow and State
The caller owns the allocated `*tm` array and must free it. `power_of_ten` is an out-parameter communicating scale shortening. `shorten()` edits label strings in place.

## Dependencies and Integration Points
It depends on libm (`floor`, `ceil`, `log10`, `pow`), C allocation/string APIs, and `tickmarks.h`. It is used by fio graph-generation components that need stable axis labels.

## Risks and Test Signals
Risks include undefined behavior when `min == max`, `nticks < 2`, nonpositive ranges, allocation failure not checked, and fixed 20-byte label buffers. The inactive `#if 0` main function documents manual test cases. Signals are plotted axis readability, no crashes for typical ranges, and correct suffix scaling.
