# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istruct.h

Purpose: extends generic Ghostscript structure/GC support with interpreter ref-aware pointer handling.

Key definitions:
- `ptr_ref_type` identifies GC pointer procedures for refs.
- `st_refs` is the structure descriptor for blocks of refs, exported for save/restore scanning.
- `gc_procs_with_refs_t` extends the common GC procedure table with relocation of ref pointers and blocks of packed/full refs.
- Macros such as `ENUM_RETURN_REF`, `RELOC_REF_PTR_VAR`, `RELOC_REFS`, and `RELOC_REF_VAR` make GC descriptors for interpreter objects with embedded refs concise.
- Ref-struct descriptor helpers support structs whose payload is actually refs, used for client data of some library objects.

This header is a small but critical adapter between the interpreter ref model and the generic movable-GC infrastructure.
