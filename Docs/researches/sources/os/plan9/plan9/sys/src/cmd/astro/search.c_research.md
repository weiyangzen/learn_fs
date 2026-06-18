# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/search.c

Searches sampled object positions for astronomical events.

Key points:
- Adds rise/set events for all objects.
- Adds solar solstice/equinox, twilight, and meteor shower events.
- Adds Moon phase events.
- Detects Mercury/Venus elongations, Moon occultations, eclipses, solar transits, and close “house” events.
- Optionally searches star occultations and satellite passes.
- Flushes sorted events at the end.

Dependencies:
- Uses `dist.c` event helpers, `occult`, `stars`, and `satels`.

Notable behavior:
- Contains visible typo text `meeteeor shouwer` in meteor event format.
