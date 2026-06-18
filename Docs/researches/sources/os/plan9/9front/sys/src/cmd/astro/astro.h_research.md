# File Research: sources/os/plan9/9front/sys/src/cmd/astro/astro.h

Shared declarations for the `astro` astronomical event program.

Important contents:
- Defines object samples (`Obj1`), object descriptors (`Obj2`), occultation interpolation state (`Occ`), event records, calendar time state, and lunar coefficient table entries.
- Declares global ephemeris state: observer location, time, nutation, Sun/Earth vectors, orbital elements, current object coordinates, and output/catalog variables.
- Declares all cross-module functions for date parsing, planet/moon/sun computation, coordinate transforms, event search, occultations, output formatting, and table summation.

The program is designed around shared globals rather than passing large state objects between modules.
