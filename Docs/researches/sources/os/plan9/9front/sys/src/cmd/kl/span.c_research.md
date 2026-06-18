# File Research: sources/os/plan9/9front/sys/src/cmd/kl/span.c

This file assigns final text addresses and implements operand classification/instruction table lookup.

Key functions:
- `span()` walks the final program list from `INITTEXT`, assigns `pc`, uses `oplook()` sizes, updates text symbol values, rounds text size, and computes `INITDAT`.
- `xdefine()` conditionally defines linker symbols.
- `regoff()` and `aclass()` classify `Adr` operands into instruction classes while computing `instoffset`, resolving extern/static/auto/param addressing and constant forms.
- `oplook()` finds the matching `Optab` row for an instruction and caches it in `p->optab`.
- `cmp()` defines class subsumption rules used for operand-class matching.
- `ocmp()` and `buildop()` sort `optab`, build per-opcode ranges, and alias many SPARC opcodes to shared table ranges.

This is the bridge between symbolic linker IR and machine encoding. It depends on accurate symbol types/values from `dodata()` and text patching from `pass.c`.
