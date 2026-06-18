# File Research: sources/os/bsd/netbsd-src/sys/sys/cdefs_elf.h

## Scope

Provides ELF object-format support macros for symbol labels, aliases, warnings, ifuncs, ID sections, link sets, and kernel cacheline annotations.

## APIs And Behavior

- Handles optional leading underscores in C labels.
- Implements symbol renaming, strong/weak aliases, weak references, weak visibility, warning references, and GNU indirect function declarations.
- Defines `__SECTIONSTRING`, `__IDSTRING`, `__RCSID`, `__COPYRIGHT`, and kernel metadata macros using ELF sections.
- Implements link set entries in `link_set_<set>` sections, including indexed array entry variants.
- Declares link set start/end symbols and count calculation.
- In kernel builds, defines `__read_mostly` and `__cacheline_aligned` section/alignment annotations.

## Dependencies

- Included by `cdefs.h` on ELF builds.

## Risks And Invariants

- ARM uses `%progbits` and non-ARM uses `@progbits`; ifunc syntax also varies.
- Link set start/stop symbol visibility and weak stop symbol handling are ABI-sensitive.
- Cacheline annotations depend on `COHERENCY_UNIT`.
