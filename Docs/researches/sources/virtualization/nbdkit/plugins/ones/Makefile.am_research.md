# File Research: sources/virtualization/nbdkit/plugins/ones/Makefile.am

## Purpose
Builds the `nbdkit-ones-plugin`.

## Main Contents
Defines `nbdkit-ones-plugin.la` from `ones.c` and the plugin header, applies nbdkit include paths, module/shared flags, optional linker script, Windows import library, and POD manpage generation.

## Dependencies
Uses common nbdkit automake rules and optional `HAVE_POD`.

## Risks and Notes
The structure mirrors the null plugin build; no feature gate surrounds it.
