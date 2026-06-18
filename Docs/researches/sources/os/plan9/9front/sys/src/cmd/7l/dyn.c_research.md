# File Research: sources/os/plan9/9front/sys/src/cmd/7l/dyn.c

Dynamic module relocation/import table support for the ARM64 linker.

Key elements:
- `Reloc` stores relocation count/capacity plus parallel arrays of relocation modes and word addresses.
- `grow` expands relocation arrays in chunks of 64 entries.
- `dynreloc` records one relocation, classifying it as absolute/relative and defined/undefined, converting byte addresses to word addresses, and keeping entries sorted.
- `sput` emits a NUL-terminated string through the linker output buffer.
- `asmdyn` emits the dynamic import table and relocation stream, then patches the table size at the start.

Important details:
- Relocation addresses must be word-aligned.
- Undefined symbols become import-relative relocation entries.
- Relocation deltas are encoded compactly using 1, 2, or 4 bytes depending on distance from the previous relocation.
- Debug `v` prints import/export counts.

Filesystem relevance: indirect. This supports dynamically loadable Plan 9 modules, not filesystem behavior.
