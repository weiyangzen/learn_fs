# File Research: sources/os/plan9/9front/sys/src/cmd/5l/pass.c

This file implements core linker middle-end passes: data layout, unresolved-symbol checks, branch resolution, instruction following/reordering, numeric parsing, rounding, and import/export table construction.

Key elements:
- `dodata()` validates data initializers, optionally marks string constants, lays out small data first, then larger data, then BSS, and defines `setR12`, `bdata`, `edata`, `end`, and `etext`.
- `undef()` reports remaining `SXREF` symbols.
- `patch()` resolves branch/call/return targets from symbols to `Prog.cond` pointers and branch offsets.
- `mkfwd()` creates skip-forward links to accelerate PC-to-`Prog` lookup during patching.
- `brloop()` and `brchain()` collapse chains of unconditional branches.
- `follow()` and `xfol()` reorder text for fallthrough, copy small followed blocks where helpful, and invert conditional branches to improve layout.
- `relinv()` maps conditional branch opcodes to their inverse.
- `atolwhex()` parses decimal, octal, and hex numeric options.
- `rnd()` rounds addresses/sizes upward.
- `import()` converts selected undefined signed symbols into import records.
- `export()` builds `_exporttab` and `.string` data containing signatures, addresses, and symbol names.

Dependencies and integration:
- Consumes symbols and `Prog` lists from `obj.c`.
- Produces data layout and control-flow state for `noops()`, `span()`, and `asmb()`.

Notable behavior:
- Data layout aligns symbols to 4 bytes and segment totals to 8 bytes.
- `follow()` may duplicate a small instruction sequence to avoid awkward control flow.
- Branches to undefined dynamic symbols become `UP` sentinel branches for later relocation handling.
- Export names are packed into `NSNAME`-sized string data chunks.

Research notes:
- This is the architecture-neutral-looking but ARM-specific linker middle-end for `5l`.
