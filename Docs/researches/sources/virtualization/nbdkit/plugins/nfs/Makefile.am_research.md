# File Research: sources/virtualization/nbdkit/plugins/nfs/Makefile.am

## Purpose
Builds the `nbdkit-nfs-plugin` when libnfs support is available.

## Main Contents
Defines `nbdkit-nfs-plugin.la` from `nfs.c` and `nbdkit-plugin.h`, adds include paths for nbdkit headers, common utilities, and replacement headers, and links against `libutils.la`, libnfs, optional GnuTLS libs, and the Windows import library. It conditionally adds the plugin linker version script and generates `nbdkit-nfs-plugin.1` from POD documentation when POD support is enabled.

## Dependencies
Gated by `HAVE_LIBNFS`; documentation generation is gated by `HAVE_POD`.

## Risks and Notes
The plugin is omitted entirely on builds without libnfs. Build linkage includes `GNUTLS_LIBS` even though the source mainly uses libnfs APIs, so configuration must keep those feature variables coherent.
