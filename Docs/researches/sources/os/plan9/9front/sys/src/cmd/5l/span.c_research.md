# File Research: sources/os/plan9/9front/sys/src/cmd/5l/span.c

This file assigns final PCs, manages literal pools, classifies operands, selects optab rows, builds opcode lookup ranges, and emits dynamic relocation records for `5l`.

Key elements:
- `span()` walks the final instruction list, assigns PCs, selects optab rows, adds literal pool entries for long constants/addresses, flushes pools when needed, computes text size, and sets `INITDAT`.
- `checkpool()`, `flushpool()`, and `addpool()` manage PC-relative literal pools and insert branch-around-pool instructions when required.
- `xdefine()` defines special symbols if still undefined.
- `regoff()` returns the computed effective offset for an address operand.
- `immrot()`, `immaddr()`, `immfloat()`, and `immhalf()` classify immediate encodability.
- `aclass()` maps `Adr` operands to the operand classes used by `optab[]`.
- `oplook()` selects the best matching `Optab` row for a `Prog`, caching the result.
- `cmp()` defines class compatibility and widening relationships.
- `ocmp()` and `buildop()` sort `optab[]`, disable unsupported V4/VFP rows, build `oprange[]`, and populate alias ranges.
- `dynreloc()` records sorted dynamic relocation entries.
- `asmdyn()` writes import and relocation metadata for dynamically loadable modules.

Dependencies and integration:
- Consumes `optab[]` from `optab.c`.
- Feeds selected `Optab` rows to `asmout()` in `asm.c`.
- Uses symbol/data layout from `pass.c` and DLM import state from `obj.c`.

Notable behavior:
- External/static addresses normally become SB-relative offsets using `BIG`; DLM mode uses different absolute/relocatable classification.
- Literal pool flushing is driven by 12-bit PC-relative span limits.
- The literal-pool logic contains an explicit historical BUG comment: after flush, it no longer refers back to prior values until out of range.
- Dynamic relocation addresses must be word-aligned and are delta-encoded later by `asmdyn()`.

Research notes:
- This file is the bridge between abstract linker IR and concrete ARM encoding constraints.
