# File Research: sources/os/plan9/9front/sys/src/cmd/8l/span.c

Instruction sizing, final text address assignment, symbol/line table emission, x86 machine-code encoding, and dynamic relocation output for `8l`.

Key functions:
- `span` iteratively sizes instructions, especially variable-width branches, until text PCs stabilize; it also aligns data start with `INITRND` and defines `etext`.
- `asmsym` and `putsymb` emit Plan 9 symbol table records for text, data, BSS, file history, frames, autos, and params.
- `asmlc` emits compressed line number tables.
- `oclass`, `prefixof`, `asmidx`, `asmand`, and `vaddr` classify operands and encode ModRM/SIB/displacement/address forms.
- `doasm` uses `optab` recipes to emit actual instruction bytes, including immediate, branch, call, MMX/SSE media, x87, and pseudo data encodings.
- `ymovtab` handles special move-family encodings not expressible in the regular optab pattern table.
- Includes byte-register workaround logic that temporarily exchanges registers when 386 byte instructions cannot address chosen registers.
- `dynreloc` and `asmdyn` collect sorted dynamic relocations and emit import/export relocation metadata for dynamically loadable modules.

Filesystem relevance: indirect. It serializes final executable bytes and metadata but has no filesystem algorithms.
