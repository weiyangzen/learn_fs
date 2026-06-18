# File Research: sources/virtualization/nbdkit/plugins/partitioning/Makefile.am

## Purpose
Builds the `partitioning` plugin, which synthesizes MBR/GPT partition tables around supplied files.

## Main Contents
Defines `nbdkit-partitioning-plugin.la` from `partitioning.c`, `partition-gpt.c`, `partition-mbr.c`, `virtual-disk.c`, `virtual-disk.h`, and the plugin header. It includes common GPT, regions, utility, replacement, and nbdkit headers, and links `libgpt.la`, `libregions.la`, `libutils.la`, and `libcompat.la`.

## Dependencies
Disabled on Windows because `device_size` is unsupported. Documentation generation is conditional on `HAVE_POD`.

## Risks and Notes
The plugin depends on shared common libraries for GPT structures and virtual region mapping, so ABI or helper changes in those common directories affect this plugin.
