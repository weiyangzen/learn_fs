# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/Makefile

## Purpose
Builds UBI test binaries and local static `libubi.a`.

## Key Elements
Sets libubi and kernel include paths, declares targets `io_update`, `volrefcnt`, `integ`, `io_paral`, `io_read`, `io_basic`, `mkvol_basic`, `mkvol_bad`, `mkvol_paral`, and `rsvol`, includes top-level `common.mk`, compiles `libubi.c` with `-DUDEV_SETTLE_HACK`, and links targets with `helpers.o` and `libubi.a`.

## Dependencies
Depends on `../../ubi-utils`, `../../include`, pthreads, and shared top-level build rules.

## Behavior/Risks
Builds its own local `libubi.a` rather than relying on a system library. `clean` explicitly removes only this static library in addition to common clean behavior.
