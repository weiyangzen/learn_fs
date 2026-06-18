# File Research: sources/local-fs/dlm/libdlm/libdlm.pc.in

## Purpose
pkg-config template for the threaded `libdlm`.

## Contents
- Substitutes `@PREFIX@` and `@LIBDIR@`.
- Exposes include path `${prefix}/include`.
- Names package `libdlm`, version `4.0.0`.
- Links with `-ldlm -lpthread`.

## Notes
- Version here is package/API metadata and does not match the Makefile soname major/minor directly.
