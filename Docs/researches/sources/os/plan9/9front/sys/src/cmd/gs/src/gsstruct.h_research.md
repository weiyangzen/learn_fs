# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstruct.h

Defines the macro framework Ghostscript modules use to describe GC-visible structures.

Key behavior:
- Documents naming conventions for structure types, typedefs, public/private descriptors, embedded structures, and array element descriptors.
- Defines pointer processing procedure tables for unmark/mark/relocate operations and standard pointer types for structs and strings.
- Defines GC roots and `public_st_gc_root_t`.
- Defines GC relocation procedure accessors used by structure-specific relocation routines.
- Provides stock no-pointer and basic table-driven enumeration/relocation declarations.
- Defines `BASIC_PTRS`, `GC_OBJ_ELT`, string element descriptors, and descriptor builders for simple, basic, composite, complex, finalizable, element-array, pointer-only, suffix-subclass, and general-subclass structures.
- Provides enumeration/relocation helper macros such as `ENUM_PTR`, `ENUM_STRING`, `RELOC_PTR`, `RELOC_STRING_VAR`, `ENUM_USING`, and `RELOC_USING`.
- Includes convenience descriptor macros for structures with fixed numbers of object/string pointers.

Dependencies:
- Includes `gsstype.h` for the underlying descriptor types and proc signatures.

Research notes:
- This is infrastructure rather than runtime policy, but many files in this group instantiate descriptors through these macros.
- The suffix/general subclass macros encode superclass offsets and additional pointer tables, so descriptor correctness depends on accurate member order and offsets.
