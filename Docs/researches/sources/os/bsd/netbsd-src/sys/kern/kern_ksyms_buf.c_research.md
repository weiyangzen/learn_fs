# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ksyms_buf.c

Read completely: 16 lines.

Provides the optional boot-time storage buffer for a copied kernel symbol table when `makeoptions_COPY_SYMTAB` is enabled.

Behavior:
- Includes `opt_copy_symtab.h` when kernel options are available.
- Defines `SYMTAB_FILLER` as the sentinel string used by `kern_ksyms.c` to detect whether a real symbol table has been copied into `db_symtab`.
- If `makeoptions_COPY_SYMTAB` is enabled and `SYMTAB_SPACE` is not defined, declares `db_symtab[]` initialized to the filler.
- If `SYMTAB_SPACE` is defined, declares a fixed-size `db_symtab[SYMTAB_SPACE]` initialized to the filler.
- Exports `db_symtabsize` as `sizeof(db_symtab)`.

Integration:
- `kern_ksyms.c` checks whether `db_symtab` still begins with the filler before loading copied symbols in `ksyms_init()`.

Risks and notes:
- This file is entirely compile-option gated; without `makeoptions_COPY_SYMTAB`, it emits no symbol buffer.
