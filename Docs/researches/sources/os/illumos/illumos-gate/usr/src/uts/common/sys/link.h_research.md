# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/link.h

## Role

ELF runtime-linker ABI header. It defines dynamic-section structures/tags, object flags, versioning structures, debugger rendezvous structures, and bootstrapping attributes used by `ld.so.1`, debuggers, link-edit tools, and compatibility code.

## Structure

- Defines `Elf32_Dyn` and, when available, `Elf64_Dyn`.
- Enumerates standard `DT_*` dynamic tags, Sun/OS-specific tags, value/address tag ranges, GNU compatibility tags, version tags, processor-specific tags, and deprecated compatibility values.
- Defines `DF_*`, `DF_P1_*`, `DF_1_*`, and obsolete `DTF_1_*` flag bits.
- Defines 32-bit and 64-bit version definition/need/symbol and syminfo structures plus version indexes and flags.
- Defines `Link_map`, `Link_map32`, `r_debug`, `r_debug32`, runtime-linker states/events/flags, and `R_DEBUG_VERSION`.
- Defines `Elf32_Boot`/`Elf64_Boot` and `EB_*` attributes for dynamic linker bootstrap, then declares `_ld_libc()`.

## Dependencies And Consumers

Non-assembly consumers include `sys/types.h` and `sys/elftypes.h`. Assembly can include the tag/constant portions without structure definitions. Consumers include runtime linker internals, debuggers via `r_debug`, ELF inspection tools, kernel runtime linker code, and compatibility layers.

## Important Details

The comments document dynamic tag encoding rules and exception ranges; tools must special-case OS and processor ranges instead of assuming even/odd pointer/value rules everywhere. Several constants remain for old binary compatibility even when illumos no longer uses them actively.

## Research Notes

Read completely: 641 lines, 23406 bytes.
