# File Research: sources/local-fs/mtd-utils/common.mk

## Purpose
Shared make rules and compiler/linker defaults for `mtd-utils`.

## Key Elements
Defines `CC`, `AR`, `RANLIB`, warning probes, large-file support, install directories, `BUILDDIR`, quiet/verbose echo helpers, archive/link/compile rules, dependency generation, and `all`, `clean`, `install` phony targets.

## Dependencies
Relies on GNU make features, compiler option probing through shell commands, and `.c` source to `.o` dependency generation with `-MMD -MF`.

## Behavior/Risks
Uses GCC extensions and assumes compatible make semantics. `SECTION_CFLAGS` probes linker garbage collection by passing linker flags through a compile test, which may vary across toolchains.
