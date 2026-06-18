# File Research: sources/local-fs/dlm/libdlm/libdlm_lt.pc.in

## Purpose
pkg-config template for the non-threaded `libdlm_lt`.

## Contents
- Substitutes `@PREFIX@` and `@LIBDIR@`.
- Names package `libdlm_lt`, version `4.0.0`.
- Links with `-ldlm_lt` and does not include pthreads.

## Notes
- Used by the Python ctypes wrapper in this group.
