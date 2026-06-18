# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/pickle.c

This file emits “pickle” helper code and complex type declarations for compiler debug/introspection output.

Key behavior:
- Maps Acid/pickle-reserved names to `$`-prefixed names with `pmap()`.
- Finds symbols associated with struct/union/enum and function types through hash-table scans.
- Initializes per-type pickle format characters.
- `picklemember()` emits code to pickle scalar, pointer, array, struct, and union fields.
- `pickletype()` emits `pickle_<type>()` functions for structs/unions or structure-offset defines under structure-debug mode.
- `picklevar()` emits Acid-style `complex` declarations for variables whose types are structs/unions, including local function scoping.

Important details:
- Output is gated by debug flag `P`, with additional suppression for nested includes when `P > 1`.
- Integer pickle codes depend on target `int`, `short`, and `long` widths.
- Arrays emit explicit loops over elements.

Filesystem relevance:
- Indirect compiler debug-output support.
