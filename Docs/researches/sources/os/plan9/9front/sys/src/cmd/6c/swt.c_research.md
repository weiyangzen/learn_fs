# File Research: sources/os/plan9/9front/sys/src/cmd/6c/swt.c

- Role: Switch lowering, bit-field load/store helpers, string/data literal emission, and object-code serialization for 6c.
- `swit1()` emits either linear compare/jump sequences for small switches or recursive binary-search comparisons for larger case tables.
- `bitload()` extracts C bit-fields by loading the containing cell, shifting, and masking/sign-extending according to field metadata.
- `bitstore()` masks, shifts, merges, writes back bit-field values, and optionally preserves the assigned value.
- `outstring()`, `sextern()`, and `gextern()` emit string chunks and global/static initializer DATA records.
- `outcode()` writes the compiler’s `Prog` list to the Plan 9 object format, including symbol caching with `zname()` and operand serialization with `zaddr()`.
- `outhist()` serializes file/line history records, including Windows path handling compatibility.
- `zaddr()` uses compact type flags for index, symbol, offset, 64-bit offset, float constant, string constant, and address type fields.
- `align()` and `maxround()` implement amd64 ABI/layout rules for struct elements, arguments, autos, and stack rounding.
