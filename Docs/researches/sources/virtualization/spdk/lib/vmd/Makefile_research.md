# File Research: sources/virtualization/spdk/lib/vmd/Makefile

## Purpose
Builds the SPDK `vmd` library.

## Key Elements
Includes SPDK common make rules, sets shared object version `8.0`, compiles `vmd.c` and `led.c`, sets `LIBNAME = vmd`, uses `spdk_vmd.map`, and includes `mk/spdk.lib.mk`.

## Dependencies
Depends on the SPDK build system rooted two directories up from this Makefile.

## Behavior/Risks
This file has no conditional source selection; the VMD library always includes both controller logic and LED support from this directory.
