# File Research: sources/os/bsd/freebsd-src/sbin/ggate/Makefile.inc

## Purpose

Shared include for GEOM Gate child Makefiles.

## Contents

Includes FreeBSD source options via:

```make
.include <src.opts.mk>
```

## Integration Notes

Provides a common options include point for `ggatec`, `ggated`, and `ggatel`.
