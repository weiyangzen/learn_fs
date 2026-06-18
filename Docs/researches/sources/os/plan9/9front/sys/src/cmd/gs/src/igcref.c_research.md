# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igcref.c

Implements GC support for Ghostscript `ref` objects and packed refs.

Key points:
- Defines special structure type descriptor `st_refs`.
- Defines shared procs for ref blocks:
  - `refs_clear_reloc`
  - `refs_set_reloc`
  - `refs_compact`
- Defines helper procs for structs containing embedded refs:
  - `ref_struct_clear_marks`
  - `ref_struct_enum_ptrs`
  - `ref_struct_reloc_ptrs`
- `ptr_ref_unmark` and `ptr_ref_mark` manage l_mark/pmark bits for full and packed refs.
- `refs_clear_marks` clears marks across mixed packed/full ref blocks.
- `refs_set_reloc`:
  - Computes freed bytes within a refs object.
  - Preserves packed-ref alignment groups.
  - Stores relocation info in packed integer values or unused `r_size` fields.
  - Handles cases where relocation cannot fit into `r_size`.
- `igc_reloc_refs` relocates the contents of marked refs, including:
  - files/devices/structs/fonts
  - dictionaries
  - arrays and packed arrays
  - names
  - strings
  - op arrays
- `igc_reloc_ref_ptr` relocates a pointer into a ref block by scanning forward for relocation metadata.
- `refs_compact` copies only marked refs, clears marks, pads alignment, creates free block space if possible, and recreates a final sentinel ref.

Dependencies and interactions:
- Uses name-table relocation helpers from `iname.h`.
- Uses string relocation macros from the GC procedure vector.
- Used directly by `igc.c`.

Risks and notes:
- The file itself describes `igc_reloc_ref_ptr` as intrinsically inefficient.
- Uses careful overlap-safe copying for refs.
- Contains architecture/alignment conditionals for packed refs.

Research relevance:
- This is the specialized compacting collector for PostScript object references, a central piece of interpreter VM correctness.
