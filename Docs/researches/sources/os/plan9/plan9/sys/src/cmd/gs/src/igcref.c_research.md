# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcref.c

Implements GC support for Ghostscript `ref` objects and packed refs.

Key points:
- Defines special structure descriptor `st_refs`.
- Defines shared procs for ref blocks: `refs_clear_reloc`, `refs_set_reloc`, and `refs_compact`.
- Defines helper procs for structs containing embedded refs: `ref_struct_clear_marks`, `ref_struct_enum_ptrs`, and `ref_struct_reloc_ptrs`.
- `ptr_ref_unmark` and `ptr_ref_mark` manage mark bits for full refs and packed refs.
- `refs_clear_marks` clears marks across mixed packed/full ref blocks.
- `refs_set_reloc` computes freed bytes, preserves packed-ref alignment groups, stores relocation in packed integer values or unused `r_size` fields, and handles relocation values too large for `r_size`.
- `igc_reloc_refs` relocates marked refs for files, devices, structs, fonts, dictionaries, arrays, packed arrays, names, strings, and op arrays.
- `igc_reloc_ref_ptr` relocates a pointer into a ref block by scanning forward for relocation metadata; comments call this intrinsically inefficient.
- `refs_compact` copies only marked refs, clears marks, pads alignment, creates a free block when possible, and recreates the final sentinel ref.
- The Plan 9 copy pads `new_size` using `new_size & (sizeof(ref) - 1)` in `refs_compact`, a power-of-two alignment mask.

Research relevance:
- Specialized compacting collector for PostScript object references, central to interpreter VM correctness.
