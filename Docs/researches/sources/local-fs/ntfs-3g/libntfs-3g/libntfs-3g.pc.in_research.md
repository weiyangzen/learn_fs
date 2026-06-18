# File Research: sources/local-fs/ntfs-3g/libntfs-3g/libntfs-3g.pc.in

## Purpose
Pkg-config template for the `libntfs-3g` library.

## Contents
Defines substituted install variables:
- `prefix`
- `exec_prefix`
- `libdir`
- `includedir`

Exports:
- `Name: libntfs-3g`
- `Description: NTFS-3G Read/Write Driver Library`
- `Version: @PACKAGE_VERSION@`
- `Cflags: -I${includedir}`
- `Libs: @LIBFUSE_LITE_LIBS@ -L${libdir} -lntfs-3g`

## Integration Points
Consumed by build/install tooling to generate a `.pc` file for downstream compilation and linking.

## Risks
Correctness depends on configure-time substitution of package version, include/lib directories, and optional FUSE-lite libraries.
