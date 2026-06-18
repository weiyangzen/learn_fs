# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdmedia.h

## Purpose

`fdmedia.h` supplies static default floppy media and drive tables used by the floppy driver: label format strings, media attributes, media geometries, drive timing profiles, and partition maps.

## Main Data

`deflabel_35` and `deflabel_525` are default ASCII label format strings for 3.5-inch and 5.25-inch floppies.

`fdtypes[]` maps each floppy format ID to `struct fdattr` values: rotational speed, interleave, read gap, and format gap.

`dfc_*` static `struct fd_char` instances describe default geometries such as 80x36, 80x21, 80x18, 80x15, 80x9, 77x8, 40x16, 40x9, 40x8, and 40x4.

`defchar[]` maps driver format IDs (`FMT_5H`, `FMT_3E`, etc.) to those geometries.

`dfd_350ED`, `dfd_350HD`, `dfd_525HD`, and `dfd_525DD` describe default drive timing and precompensation parameters.

`dpt_*` arrays define default `NDKMAP` partition maps for each geometry, normally with partition 0 as all but the last cylinder, partition 1 as the last cylinder, and partition 2 as the whole disk.

`fdparts[]` maps format IDs to default partition maps.

## Research Notes

Unlike most headers, this file defines static data directly. It is meant to be included by the floppy implementation to instantiate default media tables. Its storage relevance is the geometry-to-partition translation that determines how floppy block devices expose slices to filesystems.
