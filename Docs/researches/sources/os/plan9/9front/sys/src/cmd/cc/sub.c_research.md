# File Research: sources/os/plan9/9front/sys/src/cmd/cc/sub.c

Large compiler utility module for AST creation/printing, type construction, type compatibility, structure member lookup, conversions, diagnostics, reachability helpers, and miscellaneous semantic utilities.

Key behavior:
- `new`/`new1` allocate AST nodes and assign source line numbers.
- `prtree`/`prtree1` print annotated ASTs for debugging.
- `typ`, `copytyp`, `garbt`, `simpleg`, `simplec`, and `simplet` construct and classify compiler types from parsed specifiers.
- `stcompat`/`tcompat` validate type compatibility tables and emit diagnostics.
- `dotsearch`, `dotoffset`, and `makedot` support named and unnamed struct/union field access, including bit-field and embedded-structure extensions.
- `constas` warns about assignment through `const`-qualified types.
- `typeext` inserts implicit extensions for null pointer constants, float constant lowering, and unnamed-substructure assignment/address conversions.
- `nocast` and `nilcast` classify no-code and semantically no-op casts.
- `arith` implements usual arithmetic conversions and pointer arithmetic scaling/differencing.
- Includes helpers for shift simplification, rotate/or transforms, side-effect detection, constant classification, log2/top-bit utilities, relational constant folding, condition inversion, bit lookup, type bit merging, diagnostics, type initialization, dead-head reachability scans, mixed assignment-op checks, and unsigned-comparison casts.

Dependencies:
- Includes `cc.h`.
- Uses many compiler global tables: type width/classification arrays, compatibility tables, operator names, diagnostics state, and parser/compiler symbols.

Research notes:
- This file is the semantic glue for the compiler front end.
- It contains Plan 9 C extensions for unnamed substructures and target-width-aware pointer arithmetic.
