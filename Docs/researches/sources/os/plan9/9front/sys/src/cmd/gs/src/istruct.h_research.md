# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/istruct.h

Extends Ghostscript structure/GC support for interpreter refs. It declares `ptr_ref_procs`, the `st_refs` structure descriptor, and `gc_procs_with_refs_t`, which adds ref-pointer relocation and ref-block relocation callbacks to common GC procedures.

Provides macros for enumerating and relocating refs inside GC-managed objects: `ENUM_RETURN_REF`, `RELOC_REF_PTR_VAR`, `RELOC_REFS`, and `RELOC_REF_VAR`. It also defines descriptor helpers for structures that are allocated as structs but contain refs, such as client data attached to library objects.
