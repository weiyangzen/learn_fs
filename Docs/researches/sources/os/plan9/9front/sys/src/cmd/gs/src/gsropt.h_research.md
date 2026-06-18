# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsropt.h

Defines RasterOp, transparency, and logical-operation bit encodings shared by PCL/PostScript extensions.

Key definitions:
- `gs_rop2_t` and `gs_rop3_t` encode 2-input and 3-input Boolean RasterOps, with source, destination, and texture bit positions chosen so Boolean algebra on opcodes mirrors Boolean algebra on pixels.
- Macros transform ROP3 operations by inverting operands, pinning operands to 0 or 1, swapping source/texture, applying source or texture transparency, negating results, and testing operand use.
- `gs_logical_operation_t` packs low-byte ROP3, source/pattern transparency flags, render algorithm bits, and `lop_pdf14`.
- `lop_uses_S`, `lop_uses_T`, `lop_no_T_is_S`, `lop_no_S_is_T`, and `lop_is_idempotent` support renderer optimizations and transparency behavior.
- Declares `rop_proc_table[256]` and `rop_usage_table[256]`.

Research notes:
- `TRANSPARENCY_PER_H_P` intentionally preserves HP manual semantics, including the unusual definition where transparency flags can force source use.
- `lop_pdf14` forces logical operations to be treated as non-idempotent even though it does not directly change rendering bits.
