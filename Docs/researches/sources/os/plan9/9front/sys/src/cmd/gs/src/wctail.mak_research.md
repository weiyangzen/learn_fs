# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wctail.mak

Tail fragment common to Watcom DOS/Windows makefiles.

Key points:
- Includes version, graphics library, JPEG, zlib, libpng, JBIG2, ICC, and IJS make fragments.
- Builds auxiliary programs `echogs`, `genarch`, `genconf`, `gendev`, and `geninit` with Watcom object/link rules and temporary link scripts.
- Uses Watcom DOS extender stubs and stack options for some auxiliary programs.
- Generates blank `gconfig_.h`.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.

Dependencies and interactions:
- Depends on Watcom syntax and tool variables from `wccommon.mak`.
- Included before device/contrib/platform fragments in Watcom builds.

Research relevance:
- Completes the shared Watcom build pipeline by wiring generic libraries and build-time generators.
