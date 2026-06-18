# File Research: sources/virtualization/nbdkit/plugins/pattern/Makefile.am

## Purpose
Builds the `nbdkit-pattern-plugin`.

## Main Contents
Defines `nbdkit-pattern-plugin.la` from `pattern.c` and the plugin header, includes common utility paths, links `libutils.la` and replacement compatibility libraries, applies plugin module flags and optional linker version script, and generates the manpage from POD documentation.

## Dependencies
Uses common nbdkit automake rules and optional `HAVE_POD`.

## Risks and Notes
The plugin depends on common utility helpers for byte swapping, randomness, alignment, and cleanup behavior.
