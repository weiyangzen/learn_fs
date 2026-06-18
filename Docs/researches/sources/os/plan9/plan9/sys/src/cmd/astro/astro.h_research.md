# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/astro.h

Shared header and global state definition for the `astro` program.

Key points:
- Defines object point structures, event records, occultation interpolation structures, time conversion state, and lunar coefficient table entries.
- Declares the large global state used throughout the program: observer location, epoch variables, nutation, heliocentric/geocentric coordinates, object instances, and star input fields.
- Declares all cross-file routines for planet solvers, date conversion, event search, output, and helper math.

Dependencies:
- Uses Plan 9 libc and custom `Fmt` conversions for right ascension and declination.

Notable behavior:
- This program is global-state driven; object routines communicate through shared variables rather than explicit structs.
