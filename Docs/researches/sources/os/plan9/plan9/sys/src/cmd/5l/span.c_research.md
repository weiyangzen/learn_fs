# File Research: sources/os/plan9/plan9/sys/src/cmd/5l/span.c

This is the ARM linker span/layout and instruction selection support for `5l`. It assigns program counters, sizes instructions through `oplook`, handles `ATEXT` boundaries, updates text symbol values, rounds final text size, and sets `etext`.

A central responsibility is ARM literal pool management. `addpool`, `checkpool`, and `flushpool` collect constants needed by instructions, deduplicate pool entries, and insert branches around literal pools before 12-bit PC-relative literal loads go out of range. The implementation flushes on explicit pool points, unconditional PC writes, pool overflow, or end of program.

The file also classifies operands via `aclass`, including register, shifted-register, auto/param, extern/static, constants, branch targets, floating constants, and offset forms. This drives `oplook`, which matches instructions against `optab` using compatibility tables built by `buildop`.

It includes dynamic relocation support for dynamically loadable modules: `dynreloc` records sorted relocation addresses and `asmdyn` emits import and relocation tables.

Filesystem relevance is indirect but important: this is part of the Plan 9 toolchain used to build OS binaries. Its data/text layout, symbol resolution, relocation, and dynamic module support influence how filesystem and kernel code becomes executable images.
