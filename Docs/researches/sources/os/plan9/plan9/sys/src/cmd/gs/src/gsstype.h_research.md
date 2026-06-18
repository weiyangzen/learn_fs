# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstype.h

## Purpose
Defines the core `gs_memory_struct_type_t` descriptor type and procedure signatures used by Ghostscript's garbage-collected allocator to clear marks, enumerate pointers, relocate pointers, and finalize structures.

## Public Surface
- Opaque `gc_state_t`.
- `enum_ptr_t`: returned pointer plus optional size for string pointers.
- `EV_CONST`: compatibility macro currently defined as `const`.
- Procedure signature macros: `struct_proc_clear_marks`, `struct_proc_enum_ptrs`, `struct_proc_reloc_ptrs`, `struct_proc_finalize`.
- `gs_memory_struct_type_s`: structure descriptor containing object size, name, optional shared procedures, clear/enum/reloc/finalize callbacks, and procedure data.
- `extern_st(st)`: descriptor extern declaration macro.

## Dependencies
Uses Ghostscript typedefs for memory, structure names, pointer types, and unsigned sizes from surrounding base headers.

## Risks and Notes
- Finalizers are constrained: they must not allocate or resize managed objects and must not assume managed referents still exist.
- The descriptor definition is placed here because some compilers mishandled undefined structure types when using `extern_st`.
