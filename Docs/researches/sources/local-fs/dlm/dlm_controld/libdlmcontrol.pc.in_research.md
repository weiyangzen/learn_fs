# File Research: sources/local-fs/dlm/dlm_controld/libdlmcontrol.pc.in

This is the pkg-config template for the `libdlmcontrol` development package.

It defines:
- `prefix=@PREFIX@`
- `includedir=${prefix}/include`
- `libdir=@LIBDIR@`
- Package name `libdlmcontrol`
- Description `The dlmcontrol library`
- Version `4.0.0`
- Compile flags `-I${includedir}`
- Link flags `-L${libdir} -ldlmcontrol`

The build system substitutes `@PREFIX@` and `@LIBDIR@`. There is no conditional logic in this file.
