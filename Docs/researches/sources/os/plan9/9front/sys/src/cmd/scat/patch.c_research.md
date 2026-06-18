# File Research: sources/os/plan9/9front/sys/src/cmd/scat/patch.c

Purpose: Converts between sky coordinates and `scat` patch IDs, where each patch is roughly one square degree and RA granularity decreases near the poles.

Key routines:
- `radec`: decodes a patch ID into RA hour/minute and declination degree.
- `patcha`: converts angular RA/Dec into patch ID.
- `patch`: validates RA/Dec, adjusts declination boundaries, quantizes RA by declination-dependent `round[]`, and packs RA/Dec into a long.

Integration: Used by `scat.c` for coordinate lookup, constellation expansion, and nearby-object expansion.

Risks:
- Invalid input prints diagnostics and calls `abort`.
- Patch packing is old-format dependent: high bits carry RA index, low byte carries shifted declination.
