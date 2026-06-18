# File Research: sources/os/plan9/9front/sys/src/cmd/cc/dcl.c

Purpose: Implements declaration processing, type construction, initialization handling, struct/union layout, prototypes, scoped symbol restoration, enum handling, type signatures, and automatic initializer zeroing.

Key points:
- `dodecl` walks declarator ASTs to construct arrays, pointers, functions, bitfields, and named declarations.
- `mkstatic` maps block-local statics to unique `$block` symbols.
- `tcopy` copies typedef chains where incomplete arrays need variable-specific width.
- `doinit`, `init1`, `peekinit`, and `nextinit` process scalar, array, string, struct, union, bitfield, and designated initializers.
- Static initializers require constants or address-plus-constant forms and emit data with `gextern`.
- Automatic initializers produce assignment trees, with `contig` adding zeroing code for uninitialized gaps.
- `sualign` lays out structs and unions, including bitfield packing and target alignment hooks.
- `markdcl` and `revertdcl` implement declaration-scope stack management, including unused local/parameter warnings, volatile-use preservation, tag restoration, and label diagnostics.
- `fnproto`, `anyproto`, and `fnproto1` construct and validate function prototype type lists.
- `walkparam`, `argmark`, `fndecls`, `adecl`, `pdecl`, `xdecl`, `edecl`, and `tmerge` handle parameter, auto, external, struct field, and function declarations.
- `sametype` and `rsametype` compare type chains, with special handling for functions, arrays, structs/unions, incomplete tags, and void pointers.
- `signature` and `sign` compute type hashes for `signof`/symbol signatures.
- `dotag`, `dcllabel`, `paramconv`, and `doenum` manage tags, labels, parameter promotions, and enum constants.

Dependencies and interactions:
- Includes `cc.h`.
- Calls expression analysis in `complex`, Acid output in `acidvar/acidtype`, pickle output in `pickletype`, and codegen/data hooks such as `gextern`, `align`, `maxround`, and `exreg`.
- Uses type tables and compatibility predicates from other compiler front-end files.

Research notes:
- This is the main declaration/type system implementation for the compiler.
- Initialization code is particularly broad, supporting Plan 9 extensions such as designated initializers while maintaining old-style C behavior.
