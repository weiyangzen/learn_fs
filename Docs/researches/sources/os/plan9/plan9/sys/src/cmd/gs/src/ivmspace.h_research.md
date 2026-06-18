# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ivmspace.h

Purpose: defines interpreter VM-space attribute encoding and store-check rules for refs.

VM spaces:
- `avm_foreign`, `avm_system`, `avm_global`, and `avm_local` are encoded into ref type attributes using `r_space_bits`/`r_space_shift`.
- Helpers extract, index, and set a ref's VM space.

Store-check model:
- Object spaces are treated as generations: foreign < system < global < local.
- Storing a ref into a destination is legal only if the referenced object's generation is not younger than the destination's generation.
- Macros `store_check_space` and `store_check_dest` enforce this and return `e_invalidaccess` on violations.

The comments document PostScript's local-into-global restriction plus Ghostscript initialization exceptions for systemdict-like dictionaries and global operators, with GC-root implications.
