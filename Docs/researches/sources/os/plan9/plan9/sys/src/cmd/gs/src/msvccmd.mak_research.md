# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvccmd.mak

`msvccmd.mak` defines shared command, compiler, and linker macros for MSVC Ghostscript builds. It is included by `msvc32.mak` and `msvclib.mak`.

It handles MSVC 4 versus later differences, current-directory syntax, object/output switches, genconf options, optional assembly placeholders, a `dosdefault` target, MSVC 8 deprecation warning suppressions, CPU/FPU flags for i386/PPC/alpha branches, `NOPRIVATE` and `DEBUG` defines, precompiled-header settings, debug versus optimized compiler/linker flags, stack-check/probe flags, and special 64-bit include ordering.

The resulting macros include `GENOPT`, `CCFLAGS`, `CC`, `CPP`, `CC_`, `CC_D`, `CC_INT`, `CC_NO_WARN`, `CCAUX`, and Windows-specific compile variants. `MAKEDLL` controls whether ordinary compilation is for DLL or EXE output.

The file is a pure build-command layer. Its risk is historical compiler behavior encoded in conditionals, especially workarounds for old optimizer bugs and MSVC version-specific flags.
