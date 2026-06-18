# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/Makefile

## Purpose
Builds deprecated BSD disklabel utility `bsdlabel`.

## Main Elements
- Adds `.PATH` to `${SRCTOP}/sys/geom`.
- Installs `disktab` config.
- Builds `bsdlabel` from `bsdlabel.c` and `geom_bsd_enc.c`.
- Installs `bsdlabel.8`.
- On i386/amd64, creates `disklabel` hardlink and manpage alias.
- Links against `libgeom`.

## Dependencies And Integration
Bridges userland utility code with GEOM disklabel encoding helpers.

## Risk Notes
Only i386/amd64 get historical `disklabel` aliases.
