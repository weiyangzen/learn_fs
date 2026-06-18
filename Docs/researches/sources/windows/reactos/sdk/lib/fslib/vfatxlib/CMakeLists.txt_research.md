# File Research: sources/windows/reactos/sdk/lib/fslib/vfatxlib/CMakeLists.txt

Build definition for the VFATX library.

Key elements:
- Builds `vfatxlib` from `fatx.c`, `vfatxlib.c`, and `vfatxlib.h`.
- Adds precompiled header support using `vfatxlib.h`.
- Links `chkstk`.
- Links `-lgcc` for non-MSVC builds.
- Depends on `psdk`.

Research notes:
- The library is separate from `vfatlib`; FATX formatting is compiled as its own FMIFS-style filesystem library component.
