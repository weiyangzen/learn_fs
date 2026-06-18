# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/patch.c

Maps sky coordinates to compact patch identifiers and back.

Key functions:
- `radec` decodes a patch id into RA hour, RA minute, and declination degree.
- `patcha` converts angular RA/Dec to a patch id.
- `patch` computes the patch id from integer RA hour/minute and declination degree.

Behavior notes:
- Patch declination boundaries are adjusted so patch ranges are lower-inclusive and upper-exclusive.
- RA bins are coarser near the poles using the `round` lookup table.
- Invalid RA/Dec inputs abort after printing diagnostics.
