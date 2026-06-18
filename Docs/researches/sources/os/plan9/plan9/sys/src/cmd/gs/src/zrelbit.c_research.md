# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zrelbit.c

Relational, boolean, and bitwise PostScript operators. It implements `and`, `or`, `xor`, `not`, `bitshift`, `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `.min`, `.max`, `.identeq`, and `.identne`.

Boolean/bitwise operators dispatch based on operand types, supporting booleans and integers where PostScript allows them. `bitshift` handles positive and negative shifts with range-aware behavior. Relational operators compare numbers numerically and strings lexicographically; `obj_le` provides the shared less/equal ordering helper. `eq`/`ne` delegate to generic object equality, while identity equality uses stricter object identity semantics.

The file is low-level interpreter semantics: most complexity is exact PostScript type compatibility and correct boolean result replacement on the operand stack.
