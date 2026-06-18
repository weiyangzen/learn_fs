# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstruct.h

## Purpose
Defines Ghostscript's structure descriptor and GC pointer-enumeration macro system. Modules use these macros to declare how allocated C structs are traced, relocated, finalized, and composed from super/substructures.

## Public Surface
- Pointer procedure model: `gs_ptr_procs_s`, `ptr_struct_type`, `ptr_string_type`, `ptr_const_string_type`.
- GC root struct: `gs_gc_root_s` and `public_st_gc_root_t`.
- GC relocation procedure-vector model: `gc_procs_common_t` and `gc_proc`.
- Standard descriptors: `extern_st(st_free)`, `st_bytes`, `st_gc_root_t`, const string element descriptors.
- Descriptor declaration scopes: `public_st`, `private_st`.
- Basic GC table representation: `gc_ptr_type_index_t`, `gc_ptr_element_t`, `gc_struct_data_t`.
- Large macro families for descriptor creation, enum/reloc procedure writing, simple structures, complex structures, composites, element arrays, pointer wrappers, fixed pointer-count structures, suffix subclasses, and general subclasses.

## Descriptor Model
- Every GC-visible structure has a `gs_memory_struct_type_t` descriptor containing size, name, optional shared procedures, clear/enum/reloc/finalize procedures, and procedure data.
- Basic table-driven descriptors list pointer/string fields by offset and use shared `basic_enum_ptrs` / `basic_reloc_ptrs`.
- Composite descriptors can provide hand-written enum/reloc procedures.
- Subclass macros support two layouts: suffix subclasses where the superclass is at offset 0, and general subclasses where the superclass is a named member at a nonzero offset.

## Enumeration and Relocation Macros
- `ENUM_PTRS_BEGIN`, `ENUM_PTRS_WITH`, `ENUM_PTR`, `ENUM_STRING_PTR`, and related macros build switch-based pointer enumerators.
- `RELOC_PTRS_BEGIN`, `RELOC_PTRS_WITH`, `RELOC_PTR`, `RELOC_STRING_PTR`, and related macros build relocation procedures.
- `ENUM_USING` / `RELOC_USING` delegate enumeration/relocation to another structure descriptor, supporting embedded structures.
- Offset relocation macros handle pointers into the middle of relocatable objects.

## Structure Definition Macros
- `gs_public_st_simple` / `gs_private_st_simple`: no internal pointers.
- `gs_*_st_basic*`: table-defined pointer/string fields, optional superclass and finalization.
- `gs_*_st_composite*`: hand-written enum/reloc, optional finalization.
- `gs_*_st_element`: arrays of structures whose base descriptor has a fixed pointer count.
- `gs_*_st_ptr`: object that is itself just a pointer.
- `gs_*_st_ptrsN`, `gs_*_st_const_stringsN`, and mixed macros cover common fixed pointer/string counts.
- `gs_*_st_suffix_addN` and `gs_*_st_ptrs_addN` cover subclass descriptors with extra traceable fields.

## Dependencies
Requires `gsstype.h` and Ghostscript base memory/string typedefs. It assumes supporting functions/macros from the memory manager, GC, and compiler-compatibility layers.

## Risks and Notes
- This is macro infrastructure used across the Ghostscript library. Small changes can affect garbage collection correctness globally.
- The file documents conventions for placing structure definition, descriptor externs, and descriptor macros together; violating those conventions can hide GC descriptors or make allocation unsafe.
- Some finalization inheritance comments describe hacks and historical constraints in the descriptor format.
