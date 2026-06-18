# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/stars.c

Searches SAO star table for lunar occultations.

Key points:
- Opens `/lib/sky/estartab`.
- Limits candidates by right ascension range around Moon path.
- Parses fixed-column star data: SAO number, RA, declination, proper motion, parallax, and magnitude.
- Converts each candidate via `star`, copies it into the star object sample array, and runs `occult`.
- Emits occultation begin/end events with dark/significant flags based on magnitude.

Dependencies:
- Uses `rline`, `star`, `occult`, and event queue.

Notable behavior:
- Handles RA wraparound when Moon path crosses zero hours.
