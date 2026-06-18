# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gs.mak

Purpose: Generic Ghostscript makefile included by platform-specific makefiles.

Configuration surface: Documents required platform variables such as executable names, library/cache/doc paths, third-party library source paths, shared-library toggles, devices, features, initialization behavior, band-list settings, file/stdio implementation choices, and VM/name-table options.

Build structure: Defines generated/object directories, executable/tool paths, generated configuration headers, default/clean targets, and macros for constructing `.dev` module files using `echogs`.

Generated files: Builds `devs.tr` from platform, feature, and device `.dev` lists. Builds linker/configuration traces via `genconf`. Emits `gconfigd.h` with runtime path/version constants using `echogs`.

Dependencies and notes: This file is intentionally platform-neutral and assumes platform makefiles provide command syntax macros such as compiler invocations, delete/copy commands, object suffixes, and shell/executable prefixes.
