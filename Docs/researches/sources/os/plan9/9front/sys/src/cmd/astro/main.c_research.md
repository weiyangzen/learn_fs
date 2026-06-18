# File Research: sources/os/plan9/9front/sys/src/cmd/astro/main.c

Program entry and command-line/date/location setup for `astro`.

Important behavior:
- Initializes constants, formatters, default period/sample interval, object table, and command-line options.
- Main loop samples all objects across `NPTS+2` time points unless point/distance modes short-circuit.
- `args` handles flags, date input, delta-T input, location input, and eclipse-object selection.
- Defaults location from `/lib/sky/here`, falling back to a hard-coded Bell Labs Murray Hill location.
- `readate`, `readdt`, `readlat`, and `etdate` provide user/date helpers.

This is the scheduler that drives all ephemeris modules and event search.
