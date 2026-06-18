# File Research: sources/os/plan9/9front/sys/src/cmd/astro/search.c

Searches sampled object positions for daily astronomical events.

Important behavior:
- Adds rise/set events for all sampled solar-system objects.
- Adds solstice/equinox and meteor-shower events based on Sun position.
- Detects twilight start/end, Moon phase crossings, Mercury/Venus elongations, Moon occultations, solar/lunar eclipses, and inner-planet transits.
- Optionally searches star occultations and satellite passes.
- Flushes sorted events at the end.

This is the main event synthesis layer over the sampled ephemeris points.
