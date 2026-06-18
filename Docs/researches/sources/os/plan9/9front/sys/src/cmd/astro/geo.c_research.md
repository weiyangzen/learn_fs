# File Research: sources/os/plan9/9front/sys/src/cmd/astro/geo.c

Converts geocentric equatorial coordinates into topocentric equatorial and horizon coordinates for the configured observer.

Important behavior:
- Uses `alpha`, `delta`, `hp`, and `semi`.
- Computes local hour angle, applies diurnal parallax using geocentric latitude and Earth radius, then sets `ra`, `decl2`, `semi2`, `az`, and `el`.
- Converts azimuth/elevation to degrees at the end.

This is the final observer-location transform used by Sun, Moon, planets, stars, and satellites.
