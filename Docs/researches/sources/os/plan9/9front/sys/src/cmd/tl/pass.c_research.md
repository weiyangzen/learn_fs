# File Research: sources/os/plan9/9front/sys/src/cmd/tl/pass.c

`pass.c` implements linker middle-end passes: data layout, branch patching, code following, reachability pruning, function-pointer interworking optimization, and import/export table generation.

Data layout:
- `dodata()` validates data initializers, marks function-pointer references, optionally pulls string constants, assigns small data first, then large data, then BSS.
- Defines synthetic symbols `setR12`, `bdata`, `edata`, `end`, and `etext`.

Branch/control-flow:
- `undef()` reports unresolved externs.
- `brchain()` follows unconditional branch chains.
- `relinv()` inverts conditional branch opcodes.
- `follow()` and `xfol()` reorder code for fallthrough, copy short already-followed paths, and invert branches to improve layout.
- `patch()` resolves branch symbols/offsets, marks ARM/Thumb foreign calls, handles `SUNDEF` dynamic reloc branches, and finalizes `cond` pointers.
- `mkfwd()` builds skip-forward pointers to accelerate pc-to-prog lookup.
- `brloop()` detects branch loops.

Utilities:
- `atolwhex()` parses decimal, octal, hex, and signed numeric strings.
- `rnd()` rounds offsets to alignment.

Reachability:
- `reachable()` starts from entry and required division helpers, marks reachable text/data symbols through operand references, removes unused text/data, and marks unused symbols `SREMOVED`.

Function pointer optimization:
- `fused()`, `ckfpuse()`, `setfpuse()`, `cksymuse()`, `ckuse()`, and `setuse()` analyze function pointer uses.
- `fnptrs()` can simplify some indirect `BX O(R)` uses back to `BL O(R)` when all uses stay within a compatible ARM/Thumb domain.

Dynamic import/export:
- `import()` converts selected signed unresolved symbols into `SUNDEF` imports.
- `ckoff()` validates relocation offsets.
- `newdata()` creates synthetic data records.
- `export()` builds `_exporttab` plus `.string` storage for exported symbol signatures, addresses, and names.

Risk notes:
- `reachable()` has a suspicious path when removing unused data: after removing from the head, it later uses `prevt->link`, which assumes `prevt` is non-nil.
- Function-pointer simplification is conservative by default but can be relaxed with debug flag `F`.
- Import/export layout depends on `Roffset`/`Rindex` bit packing from `l.h`.
