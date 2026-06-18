# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ipacked.h

Packed-array encoding definitions for Ghostscript refs.

Key behavior:
- Documents the 16-bit `ref_packed` format used in `t_mixedarray` and `t_shortarray`.
- Defines packed types for full refs, executable operators, integers, literal names, and executable names.
- Defines packed tag/value masks and helper predicates such as `r_is_packed`, `r_packed_is_name`, and `r_packed_is_exec_name`.
- Defines packed integer range as signed 12-bit values biased by `packed_min_intval`.
- Defines packed-name maximum index as the 12-bit value mask.
- Defines packed mark-bit helpers for GC.
- Defines `packed_next` to advance by either one packed slot or a full `ref` width.
- Defines `ref_array_packing` storage through `i_ctx_p->array_packing`.

Research notes:
- The comments state that `zpacked.c` and `interp.c` know representation details beyond this header.
- Alignment constraints drive mixed-array construction: preceding packed elements may be expanded so full refs remain correctly aligned.
