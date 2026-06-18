# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/Makefile

Builds the local GEOM Gate provider utility `ggatel`.

Key contents:
- Adds `.PATH` for shared ggate sources.
- Builds from `ggatel.c` and shared `ggate.c`.
- Installs `ggatel.8`.
- Assigns package `ggate`.
- Defines `LIBGEOM`, enabling shared provider-listing code.
- Includes shared headers and links `geom` and `util`.

Unlike `ggated`, this target does not link pthread because `ggatel` serves synchronously in one worker loop.
