# File Research: sources/os/plan9/9front/sys/src/cmd/cc/acid.c

Purpose: Emits Acid debugger type and variable descriptions from the C compiler front end.

Key points:
- `amap` maps C identifiers that collide with Acid keywords to `$`-prefixed Acid names.
- `acidsue` finds the symbol naming a struct/union/enum type.
- `acidfun` finds the symbol for a function type.
- `acidinit` maps compiler type codes to Acid format characters, adjusting for target `int` and pointer widths.
- `acidmember` emits aggregate member descriptions or printer code.
- `acidtype` emits `sizeof`, `aggr`, and `defn` blocks for structs/unions when debug flag `a` is enabled; with debug `s`, emits assembler-style member offset defines.
- `acidvar` emits Acid `complex` declarations for variables whose effective type is a struct/union.

Dependencies and interactions:
- Uses compiler globals from `cc.h`, including `hash`, `types`, `debug`, `outbuf`, `iostack`, and `thisfn`.
- Called from declaration code in `dcl.c`.

Research notes:
- Acid output is debug side-channel behavior controlled by compiler debug flags.
- The implementation scans global symbol hash tables, so it is tightly coupled to the compiler symbol model.
