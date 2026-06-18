# File Research: sources/os/bsd/freebsd-src/sbin/geom/Makefile

## Purpose

Builds the generic `geom` command-line utility and its shared helper source.

## Build Definition

- Program: `geom`
- Sources: `geom.c`, `subr.c`
- Manual: `geom.8`
- Includes core and top-level geom directories.
- Defines `GEOM_CLASS_DIR`.
- Links `libgeom`, `libutil`, and `libxo`.

## Conditional Build

- In rescue builds, statically includes `geom_label.c` and `geom_part.c`, suppresses the manual, and defines `STATIC_GEOM_CLASSES`.
- Otherwise includes `lib/geom/Makefile.classes` and creates `g<class>` hardlinks for each GEOM class.

## Integration Notes

This Makefile connects the generic dispatcher in `core/geom.c` with class-specific shared libraries or static rescue implementations.
