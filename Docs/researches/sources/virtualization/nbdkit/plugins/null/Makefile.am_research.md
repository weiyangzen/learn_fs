# File Research: sources/virtualization/nbdkit/plugins/null/Makefile.am

## Purpose
Builds the always-available `nbdkit-null-plugin`.

## Main Contents
Defines `nbdkit-null-plugin.la` from `null.c` and the public plugin header, includes generated/source nbdkit headers, links the Windows import library when needed, applies module/shared libtool flags, conditionally applies the linker version script, and generates `nbdkit-null-plugin.1` from POD documentation.

## Dependencies
Uses common nbdkit automake rules and optional `HAVE_POD`.

## Risks and Notes
No feature gate surrounds the plugin, so it is expected to build on all supported platforms.
